"""
FILE: backend/models/database.py
PURPOSE: SQLite storage - PRIVACY-FIRST by design.

Stored:  assessment_id, overall_score, risk_level, created_at, category scores,
         finding types (+ short generic text) and the static recommendation catalogue.
NEVER stored: questionnaire answers, phone, email, address, birth date,
         passwords, exact location, messages, IP addresses.
"""
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from ..config import Config
from ..knowledge_base import KB

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id TEXT PRIMARY KEY,
    overall_score INTEGER NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
    risk_level    TEXT    NOT NULL CHECK (risk_level IN ('LOW','MODERATE','HIGH','CRITICAL')),
    created_at    TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS category_scores (
    category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    score    INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100)
);
CREATE TABLE IF NOT EXISTS findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    finding_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    impact_points REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_type TEXT NOT NULL UNIQUE,
    recommendation TEXT NOT NULL,
    priority TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cat_assessment ON category_scores(assessment_id);
CREATE INDEX IF NOT EXISTS idx_find_assessment ON findings(assessment_id);
"""


@contextmanager
def connect(db_path=None):
    conn = sqlite3.connect(db_path or Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=None):
    with connect(db_path) as c:
        c.executescript(SCHEMA)
        for ftype, t in KB.items():  # static catalogue, no user data
            c.execute("INSERT OR REPLACE INTO recommendations (finding_type, recommendation, priority) "
                      "VALUES (?,?,?)", (ftype, t[2], t[3]))


def new_assessment_id() -> str:
    return "PRA-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(6).upper()


def save_assessment(view: dict, db_path=None) -> dict:
    aid = new_assessment_id()
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    with connect(db_path) as c:
        c.execute("INSERT INTO assessments VALUES (?,?,?,?)",
                  (aid, view["overall_score"], view["risk_level"], created))
        c.executemany("INSERT INTO category_scores (assessment_id, category, score) VALUES (?,?,?)",
                      [(aid, s["key"], s["score"]) for s in view["category_scores"]])
        c.executemany("INSERT INTO findings (assessment_id, category, finding_type, severity, description, impact_points) "
                      "VALUES (?,?,?,?,?,?)",
                      [(aid, f["category"], f["finding_type"], f["severity"], f["description"], f["impact_points"])
                       for f in view["findings"]])
    return {"assessment_id": aid, "created_at": created}


def load_assessment(aid: str, db_path=None):
    """Return raw stored data or None."""
    with connect(db_path) as c:
        a = c.execute("SELECT * FROM assessments WHERE assessment_id=?", (aid,)).fetchone()
        if not a:
            return None
        cats = {r["category"]: r["score"] for r in
                c.execute("SELECT category, score FROM category_scores WHERE assessment_id=? ORDER BY category_score_id", (aid,))}
        finds = [dict(r) for r in c.execute(
            "SELECT category, finding_type, severity, description, impact_points FROM findings "
            "WHERE assessment_id=? ORDER BY impact_points DESC, finding_id", (aid,))]
    for f in finds:
        f["title"] = KB[f["finding_type"]][0]
    return {"assessment_id": a["assessment_id"], "overall_score": a["overall_score"],
            "risk_level": a["risk_level"], "created_at": a["created_at"],
            "category_scores": cats, "findings": finds}


def delete_assessment(aid: str, db_path=None) -> bool:
    with connect(db_path) as c:
        return c.execute("DELETE FROM assessments WHERE assessment_id=?", (aid,)).rowcount > 0


def purge_older_than(days: int, db_path=None) -> int:
    """Retention limitation: delete assessments older than N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with connect(db_path) as c:
        return c.execute("DELETE FROM assessments WHERE created_at < ?", (cutoff,)).rowcount


def live_stats(db_path=None) -> dict:
    with connect(db_path) as c:
        r = c.execute("SELECT COUNT(*) n, AVG(overall_score) a FROM assessments").fetchone()
    return {"count": r["n"], "average": round(r["a"], 1) if r["a"] is not None else None}


def get_recommendations_for(finding_types, db_path=None):
    with connect(db_path) as c:
        marks = ",".join("?" * len(finding_types)) or "NULL"
        return [dict(r) for r in c.execute(
            f"SELECT finding_type, recommendation, priority FROM recommendations WHERE finding_type IN ({marks})",
            list(finding_types))]
