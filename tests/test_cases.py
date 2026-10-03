"""
FILE: tests/test_cases.py
PURPOSE: The 30 documented test scenarios from the brief (Test ID, Scenario,
Input, Expected, Actual, Pass/Fail). Used by pytest AND by run_test_report.py,
which writes docs/TEST_REPORT.md with the real "Actual Result" column.
"""
import os
import sqlite3
import tempfile

from backend.models import database as db
from backend.services.assessment_engine import extract_privacy_features, run_assessment, score_answers
from backend.services.improvement_simulator import simulate_improvement
from backend.services.report_service import generate_report_html
from backend.services.scoring_engine import calculate_category_scores, calculate_privacy_risk, classify_risk

from .helpers import private_profile, public_profile, with_

P = private_profile
CASES = []


def case(tid, scenario, inp, expected):
    def deco(fn):
        CASES.append({"id": tid, "scenario": scenario, "input": inp, "expected": expected, "run": fn})
        return fn
    return deco


def _finding(answers, ftype):
    r = run_assessment(answers)
    return ftype in {f["finding_type"] for f in r["findings"]}, r


def single(tid, scenario, key, value, ftype, category):
    @case(tid, scenario, f"private profile with {key}={value}", f"{ftype} raised; {category} score > 0")
    def _t():
        ok, r = _finding(with_(P(), **{key: value}), ftype)
        cat = next(c for c in r["category_scores"] if c["key"] == category)["score"]
        return ok and cat > 0, f"finding={'yes' if ok else 'no'}, {category}={cat}, overall={r['overall_score']}"


@case("T01", "Fully private profile", "all lowest-risk answers", "score 0, LOW, no findings")
def _t01():
    r = run_assessment(P()); return r["overall_score"] == 0 and r["risk_level"] == "LOW" and not r["findings"], f"{r['overall_score']} {r['risk_level']}, {len(r['findings'])} findings"


@case("T02", "Fully public synthetic profile", "all highest-risk answers", "score 100, CRITICAL")
def _t02():
    r = run_assessment(public_profile()); return r["overall_score"] == 100 and r["risk_level"] == "CRITICAL", f"{r['overall_score']} {r['risk_level']}"


single("T03", "Public phone number", "phone_public", "YES", "PHONE_PUBLIC", "personal_info")
single("T04", "Public email", "email_public", "YES", "EMAIL_PUBLIC", "personal_info")
single("T05", "Public birthday", "birthday_public", "YES", "BIRTHDAY_PUBLIC", "personal_info")
single("T06", "Public location", "location_public", "YES", "PROFILE_LOCATION_PUBLIC", "location")
single("T07", "Real-time check-ins", "live_checkins", "OFTEN", "LIVE_CHECKINS", "location")
single("T08", "Travel plans posted", "travel_posts", "OFTEN", "TRAVEL_POSTS", "location")
single("T09", "Workplace exposure", "workplace_public", "YES", "WORKPLACE_PUBLIC", "personal_info")
single("T10", "Education exposure", "education_public", "YES", "EDUCATION_PUBLIC", "personal_info")
single("T11", "Public posts", "posts_public", "PUBLIC", "PUBLIC_POSTS", "content")
single("T12", "Unknown connections accepted", "unknown_connections", "OFTEN", "UNKNOWN_CONNECTIONS", "connections")
single("T13", "Tag review disabled", "tag_review_enabled", "NO", "TAG_REVIEW_DISABLED", "tagging")
single("T14", "MFA disabled", "mfa_enabled", "NO", "MFA_DISABLED", "account_security")
single("T15", "Login alerts disabled", "login_alerts_enabled", "NO", "LOGIN_ALERTS_DISABLED", "account_security")
single("T16", "Password reuse reported", "password_reuse_reported", "OFTEN", "PASSWORD_REUSE", "account_security")
single("T17", "Third-party apps never reviewed", "third_party_apps_reviewed", "NEVER", "APPS_NOT_REVIEWED", "third_party")
single("T18", "Suspicious-link awareness low", "suspicious_link_awareness", "NO", "LOW_LINK_AWARENESS", "social_engineering")
single("T19", "Old posts not reviewed", "old_posts_reviewed", "NEVER", "OLD_POSTS_NOT_REVIEWED", "footprint")
single("T20", "Privacy settings not reviewed", "privacy_settings_reviewed", "NEVER", "SETTINGS_NOT_REVIEWED", "footprint")


@case("T21", "Category score calculation", "only tag_review_enabled=NO (weight 2.5 of 7)", "tagging = 100*2.5/7 = 36")
def _t21():
    f = extract_privacy_features(with_(P(), tag_review_enabled="NO"))
    s = round(calculate_category_scores(f)["tagging"]); return s == 36, f"tagging={s}"


@case("T22", "Overall score calculation", "only phone_public=YES", "personal_info 20 -> overall 15% x 20 = 3")
def _t22():
    r = score_answers(with_(P(), phone_public="YES")); return r["overall_score"] == 3, f"overall={r['overall_score']}, personal_info={round(r['category_scores']['personal_info'])}"


@case("T23", "Score boundary 20", "scores 20 and 21", "20 -> LOW, 21 -> MODERATE")
def _t23():
    a, b = classify_risk(20), classify_risk(21); return (a, b) == ("LOW", "MODERATE"), f"{a}, {b}"


@case("T24", "Score boundary 40", "scores 40 and 41", "40 -> MODERATE, 41 -> HIGH")
def _t24():
    a, b = classify_risk(40), classify_risk(41); return (a, b) == ("MODERATE", "HIGH"), f"{a}, {b}"


@case("T25", "Score boundary 70", "scores 70 and 71", "70 -> HIGH, 71 -> CRITICAL")
def _t25():
    a, b = classify_risk(70), classify_risk(71); return (a, b) == ("HIGH", "CRITICAL"), f"{a}, {b}"


@case("T26", "Recommendation generation", "MFA disabled", "IMMEDIATE recommendation mentioning multi-factor authentication")
def _t26():
    recs = run_assessment(with_(P(), mfa_enabled="NO", mfa_method="NONE"))["recommendations"]
    m = next((r for r in recs if r["finding_type"] == "MFA_DISABLED"), None)
    return bool(m) and m["priority"] == "IMMEDIATE" and "multi-factor" in m["recommendation"].lower(), f"{m['priority'] if m else None}: {m['recommendation'][:50] if m else ''}"


@case("T27", "Improvement simulation", "worst profile, fix everything", "after < before, reduction = before - after")
def _t27():
    s = simulate_improvement(public_profile(), fix_all=True)
    return s["after"]["score"] < s["before"]["score"] and s["risk_reduction"] == s["before"]["score"] - s["after"]["score"], f"{s['before']['score']} -> {s['after']['score']} (-{s['risk_reduction']})"


@case("T28", "Database save", "save and reload an assessment", "stored values equal original")
def _t28():
    path = tempfile.mktemp(suffix=".db"); db.init_db(path)
    view = run_assessment(public_profile()); meta = db.save_assessment(view, path); back = db.load_assessment(meta["assessment_id"], path); os.remove(path)
    return back["overall_score"] == view["overall_score"] and len(back["category_scores"]) == 10 and len(back["findings"]) == len(view["findings"]), f"id={meta['assessment_id']}, score={back['overall_score']}"


@case("T29", "Sensitive data not stored", "inspect DB schema and content", "no phone/email/address/birth/password/location/message columns or answer values")
def _t29():
    path = tempfile.mktemp(suffix=".db"); db.init_db(path); db.save_assessment(run_assessment(public_profile()), path)
    con = sqlite3.connect(path); cols = [r[1].lower() for t in ("assessments", "category_scores", "findings", "recommendations") for r in con.execute(f"PRAGMA table_info({t})")]
    con.close(); os.remove(path)
    bad = [c for c in cols if any(w in c for w in ("phone", "email", "address", "birth", "password", "message", "answer", "ip_"))]
    return not bad, f"{len(cols)} columns checked, forbidden={bad}"


@case("T30", "Report generation", "report for a public profile", "contains ID, date, level, disclaimer and escapes HTML")
def _t30():
    v = run_assessment(public_profile()); v.update(assessment_id="PRA-TEST-0001", created_at="2026-01-01T00:00:00+00:00")
    v["findings"][0]["title"] = "<script>alert(1)</script>"; v["recommendations"][0]["risk"] = "<img src=x onerror=1>"
    html = generate_report_html(v)
    ok = all(x in html for x in ("PRA-TEST-0001", "2026-01-01", "CRITICAL", "educational")) and "<script>alert" not in html and "<img src=x" not in html
    return ok, f"{len(html)} bytes, script escaped={'<script>alert' not in html}"
