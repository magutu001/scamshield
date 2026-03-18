import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Request

from app.models import LoginRequest, RuleUpdate
from app.database import get_db
from app.auth import require_admin, USER_SESSIONS, PENDING_CODES
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_TOKEN

router = APIRouter()


@router.post("/api/admin-login")
def admin_login(req: LoginRequest):
    if req.email == ADMIN_EMAIL and req.password == ADMIN_PASSWORD:
        return {"success": True, "token": ADMIN_TOKEN}
    return {"success": False}


# ── Rules ──────────────────────────────────────────────────────────────────────

@router.get("/api/rules")
def get_rules(request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    return [dict(r) for r in db.execute("SELECT * FROM regex_rules ORDER BY rule_id").fetchall()]


@router.post("/api/rules")
def add_rule(rule: RuleUpdate, request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    cur = db.execute(
        "INSERT INTO regex_rules(name,pattern,weight,category,active_flag) VALUES(?,?,?,?,?)",
        (rule.name, rule.pattern, rule.weight, rule.category, rule.active_flag)
    )
    db.commit()
    return {"message": "Rule added", "rule_id": cur.lastrowid}


@router.put("/api/rules/{rule_id}")
def update_rule(rule_id: int, rule: RuleUpdate, request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    if not db.execute("SELECT rule_id FROM regex_rules WHERE rule_id=?", (rule_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Rule not found")
    db.execute(
        "UPDATE regex_rules SET name=?,pattern=?,weight=?,category=?,active_flag=? WHERE rule_id=?",
        (rule.name, rule.pattern, rule.weight, rule.category, rule.active_flag, rule_id)
    )
    db.commit()
    return {"message": "Rule updated"}


@router.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    if not db.execute("SELECT rule_id FROM regex_rules WHERE rule_id=?", (rule_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Rule not found")
    db.execute("DELETE FROM regex_rules WHERE rule_id=?", (rule_id,))
    db.commit()
    return {"message": "Rule deleted"}


# ── Users ──────────────────────────────────────────────────────────────────────

@router.get("/api/admin/users")
def get_all_users(request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    rows = db.execute(
        "SELECT user_id,name,email,role,created_date FROM users ORDER BY created_date DESC"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/api/admin/history")
def get_all_history(request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    rows = db.execute("""
        SELECT ja.advert_id, ja.title, ja.domain, ja.post_date,
               ar.scam_score, ar.verdict, ar.analyzed_date,
               COALESCE(u.name, 'Guest') as user_name
        FROM job_adverts ja
        JOIN analysis_results ar ON ja.advert_id = ar.advert_id
        LEFT JOIN users u ON ja.user_id = u.user_id
        ORDER BY ar.analyzed_date DESC LIMIT 100
    """).fetchall()
    return [dict(r) for r in rows]


@router.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_admin(request)
    user = db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = dict(user)
    if user_dict["role"] == "Admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin account")

    # Revoke all active sessions
    for t in [t for t, s in USER_SESSIONS.items() if s.get("user_id") == user_id]:
        USER_SESSIONS.pop(t, None)

    # Clear any pending registration code
    PENDING_CODES.pop(user_dict["email"], None)

    # Delete all user data
    advert_ids = [r[0] for r in db.execute(
        "SELECT advert_id FROM job_adverts WHERE user_id=?", (user_id,)
    ).fetchall()]
    for aid in advert_ids:
        db.execute("DELETE FROM analysis_results WHERE advert_id=?", (aid,))
        db.execute("DELETE FROM domain_checks WHERE advert_id=?", (aid,))
    db.execute("DELETE FROM job_adverts WHERE user_id=?", (user_id,))
    db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    db.commit()
    return {"message": "User deleted successfully"}
