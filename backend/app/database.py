import sqlite3
from app.config import DB_PATH


def get_db():
    """FastAPI dependency — yields a DB connection per request."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Create all tables and seed default detection rules on first run."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        email         TEXT    UNIQUE NOT NULL,
        password      TEXT    NOT NULL,
        role          TEXT    DEFAULT 'JobSeeker',
        created_date  TEXT    DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS job_adverts(
        advert_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT,
        description TEXT    NOT NULL,
        domain      TEXT,
        post_date   TEXT    DEFAULT CURRENT_TIMESTAMP,
        user_id     INTEGER)""")

    c.execute("""CREATE TABLE IF NOT EXISTS analysis_results(
        result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        advert_id     INTEGER NOT NULL,
        scam_score    INTEGER,
        verdict       TEXT,
        flags         TEXT,
        analyzed_date TEXT    DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS domain_checks(
        check_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        advert_id  INTEGER NOT NULL,
        ssl_valid  INTEGER,
        domain_age INTEGER,
        whois_info TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS regex_rules(
        rule_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pattern     TEXT    NOT NULL,
        weight      INTEGER DEFAULT 10,
        category    TEXT    DEFAULT 'text',
        active_flag INTEGER DEFAULT 1)""")

    # Seed default rules only if table is empty
    if c.execute("SELECT COUNT(*) FROM regex_rules").fetchone()[0] == 0:
        rules = [
            ("Upfront Payment Request",
             r"(?i)(pay|send|deposit|transfer|fee|registration fee|processing fee|upfront|advance payment)",
             25, "payment"),
            ("Unrealistic Salary",
             r"(?i)(earn \$[\d,]+|ksh[\s]?[\d,]+\s*per\s*(day|hour)|100[k,]000|salary.*guaranteed|weekly pay.*high)",
             20, "salary"),
            ("Urgent Hiring Language",
             r"(?i)(urgent(ly)?|immediate(ly)?|asap|apply now|limited slots|few positions left|hiring today)",
             15, "urgency"),
            ("No Experience Required",
             r"(?i)(no experience (needed|required)|work from home.*easy|anyone can|no qualifications)",
             15, "qualifications"),
            ("Suspicious Contact Method",
             r"(?i)(whatsapp only|call this number|telegram|contact us on|send cv to gmail|yahoo\.com|hotmail\.com)",
             20, "contact"),
            ("Vague Job Description",
             r"(?i)(data entry.*home|online (tasks|jobs)|flexible (hours|schedule).*easy money|passive income)",
             10, "description"),
            ("Request for Personal Info",
             r"(?i)(send (your )?(id|passport|national id|bank details|pin|account number))",
             25, "personal_info"),
            ("Work from Home Scam",
             r"(?i)(work from home.*per (day|hour|week)|make money.*home|earn.*sitting at home)",
             15, "wfh"),
            ("Too Good to Be True",
             r"(?i)(guaranteed (income|earnings|salary)|no risk|100% (legitimate|genuine|real)|double your)",
             20, "tbgt"),
            ("Fake Company Signals",
             r"(?i)(international (company|organization)|UN jobs|NGO.*hiring|multinational.*urgent)",
             15, "company"),
        ]
        c.executemany(
            "INSERT INTO regex_rules(name,pattern,weight,category) VALUES(?,?,?,?)",
            rules
        )

    conn.commit()
    conn.close()
