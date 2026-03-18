import sqlite3
from fastapi import APIRouter, Depends, Request

from app.models import AnalyzeRequest
from app.database import get_db
from app.auth import get_current_user
from app.detection import analyze_text, check_domain, calculate_verdict

router = APIRouter()


@router.post("/api/analyze")
def analyze(req: AnalyzeRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    rules   = [dict(r) for r in db.execute("SELECT * FROM regex_rules WHERE active_flag=1").fetchall()]
    tr      = analyze_text(req.description, rules)
    di      = check_domain(req.domain or "")
    vr      = calculate_verdict(tr["score"], di)
    user    = get_current_user(request)
    user_id = user["user_id"] if user else None

    cur = db.execute(
        "INSERT INTO job_adverts(title,description,domain,user_id) VALUES(?,?,?,?)",
        (req.title or "Untitled", req.description, req.domain or "", user_id)
    )
    aid = cur.lastrowid
    db.execute(
        "INSERT INTO analysis_results(advert_id,scam_score,verdict,flags) VALUES(?,?,?,?)",
        (aid, vr["total_score"], vr["verdict"], str(tr["flags"] + vr["domain_flags"]))
    )
    db.execute(
        "INSERT INTO domain_checks(advert_id,ssl_valid,domain_age,whois_info) VALUES(?,?,?,?)",
        (aid, int(di["ssl_valid"]), di["domain_age"], di["whois_info"])
    )
    db.commit()

    return {
        "advert_id":    aid,
        "title":        req.title or "Untitled",
        "score":        vr["total_score"],
        "verdict":      vr["verdict"],
        "color":        vr["color"],
        "emoji":        vr["emoji"],
        "advice":       vr["advice"],
        "text_flags":   tr["flags"],
        "domain_flags": vr["domain_flags"],
        "domain_info":  di
    }


@router.get("/api/history")
def get_history(request: Request, db: sqlite3.Connection = Depends(get_db)):
    user = get_current_user(request)
    if user:
        rows = db.execute("""
            SELECT ja.advert_id, ja.title, ja.domain, ja.post_date,
                   ar.scam_score, ar.verdict, ar.analyzed_date
            FROM job_adverts ja
            JOIN analysis_results ar ON ja.advert_id = ar.advert_id
            WHERE ja.user_id = ?
            ORDER BY ar.analyzed_date DESC LIMIT 50
        """, (user["user_id"],)).fetchall()
    else:
        rows = db.execute("""
            SELECT ja.advert_id, ja.title, ja.domain, ja.post_date,
                   ar.scam_score, ar.verdict, ar.analyzed_date
            FROM job_adverts ja
            JOIN analysis_results ar ON ja.advert_id = ar.advert_id
            ORDER BY ar.analyzed_date DESC LIMIT 50
        """).fetchall()
    return [dict(r) for r in rows]


@router.get("/api/stats")
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    return {
        "total":     db.execute("SELECT COUNT(*) as c FROM analysis_results").fetchone()["c"],
        "high_risk": db.execute("SELECT COUNT(*) as c FROM analysis_results WHERE verdict='HIGH RISK'").fetchone()["c"],
        "caution":   db.execute("SELECT COUNT(*) as c FROM analysis_results WHERE verdict='NEEDS CAUTION'").fetchone()["c"],
        "safe":      db.execute("SELECT COUNT(*) as c FROM analysis_results WHERE verdict='LIKELY SAFE'").fetchone()["c"]
    }
