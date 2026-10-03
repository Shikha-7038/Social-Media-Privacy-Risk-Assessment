"""
Privacy & security tests (brief section 34). Each test documents WHY it exists.
"""
import re
import sqlite3

from backend.questionnaire import QUESTIONS
from .helpers import private_profile, public_profile


def post(client, answers):
    return client.post("/api/assessment", json={"answers": answers})


# ---- input validation -----------------------------------------------------
def test_rejects_unknown_question(client):
    a = private_profile(); a["ZZ99"] = "YES"
    assert post(client, a).status_code == 400


def test_rejects_invalid_option(client):
    a = private_profile(); a["A1"] = "EVERYONE_AND_MORE"
    assert post(client, a).status_code == 400


def test_rejects_missing_answers(client):
    a = private_profile(); a.pop("A1")
    r = post(client, a); assert r.status_code == 400 and "A1" in str(r.get_json())


def test_rejects_non_json_and_wrong_types(client):
    assert client.post("/api/assessment", data="x", content_type="text/plain").status_code == 400
    assert client.post("/api/assessment", json={"answers": [1, 2]}).status_code == 400
    a = private_profile(); a["A1"] = {"$ne": 1}
    assert post(client, a).status_code == 400


def test_free_text_and_pii_fields_are_rejected(client):
    a = private_profile(); a["phone_number"] = "+1 555 0100"
    assert post(client, a).status_code == 400


# ---- XSS ------------------------------------------------------------------
def test_xss_payload_not_reflected(client):
    a = private_profile(); a["A1"] = "<script>alert(1)</script>"
    r = post(client, a)
    assert r.status_code == 400 and b"<script>" not in r.data
    assert r.mimetype == "application/json"


def test_report_is_escaped_and_locked_down(client):
    aid = post(client, public_profile()).get_json()["assessment_id"]
    r = client.get(f"/api/assessment/{aid}/report")
    assert r.status_code == 200 and "default-src 'none'" in r.headers["Content-Security-Policy"]
    assert b"<script" not in r.data.lower()


# ---- storage / privacy-by-design -----------------------------------------
def test_database_stores_no_answers_or_pii(client, app):
    post(client, public_profile())
    con = sqlite3.connect(app.config["DATABASE_PATH"])
    dump = "\n".join(str(row) for t in ("assessments", "category_scores", "findings") for row in con.execute(f"SELECT * FROM {t}")).lower()
    cols = [r[1].lower() for t in ("assessments", "category_scores", "findings") for r in con.execute(f"PRAGMA table_info({t})")]
    con.close()
    for word in ("phone", "email", "address", "birth", "password", "location_exact", "message"):
        assert not any(word == c or c.startswith(word) for c in cols)
    assert "'yes'" not in dump and "'often'" not in dump       # raw answers never persisted


def test_no_ip_address_persisted(client, app):
    post(client, private_profile())
    con = sqlite3.connect(app.config["DATABASE_PATH"])
    blob = str(list(con.execute("SELECT * FROM assessments")))
    assert not re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", blob)


def test_data_deletion(client):
    aid = post(client, public_profile()).get_json()["assessment_id"]
    assert client.get(f"/api/assessment/{aid}").status_code == 200
    assert client.delete(f"/api/assessment/{aid}").status_code == 200
    assert client.get(f"/api/assessment/{aid}").status_code == 404
    assert client.delete(f"/api/assessment/{aid}").status_code == 404


def test_deletion_cascades_to_child_tables(client, app):
    aid = post(client, public_profile()).get_json()["assessment_id"]; client.delete(f"/api/assessment/{aid}")
    con = sqlite3.connect(app.config["DATABASE_PATH"])
    assert con.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM category_scores").fetchone()[0] == 0


def test_retention_purge(app):
    from backend.models import database as db
    assert db.purge_older_than(30, app.config["DATABASE_PATH"]) == 0


# ---- API hardening --------------------------------------------------------
def test_bad_id_formats_and_sqli_attempts(client):
    for bad in ("1;DROP TABLE assessments", "' OR '1'='1", "../../etc/passwd", "x"):
        assert client.get(f"/api/assessment/{bad}").status_code in (400, 404)
    assert client.get("/api/assessment/PRA-20260101-ABCDEF123456").status_code == 404


def test_security_headers(client):
    r = client.get("/api/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff" and r.headers["X-Frame-Options"] == "DENY"
    assert "script-src 'self'" in r.headers["Content-Security-Policy"] and r.headers["Cache-Control"] == "no-store"


def test_oversized_body_rejected(client):
    r = client.post("/api/assessment", data=b"{" + b"a" * 200_000, content_type="application/json")
    assert r.status_code in (400, 413)


def test_rate_limiting(tmp_path):
    from backend.app import create_app
    c = create_app({"DATABASE_PATH": str(tmp_path / "r.db"), "RATE_LIMIT": 1000, "WRITE_RATE_LIMIT": 3}).test_client()
    codes = [c.post("/api/assessment", json={"answers": private_profile()}).status_code for _ in range(5)]
    assert codes[:3] == [201, 201, 201] and codes[3] == 429


def test_secrets_not_committed():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    assert (root / ".env.example").exists() and not (root / ".env").exists()
    assert ".env" in (root / ".gitignore").read_text()


# ---- simulator / API behaviour -------------------------------------------
def test_simulate_endpoint(client):
    r = client.post("/api/assessment/simulate-improvement", json={"answers": public_profile(), "fix_findings": ["MFA_DISABLED", "PHONE_PUBLIC"]})
    d = r.get_json(); assert r.status_code == 200 and d["risk_reduction"] > 0 and "not a guarantee" in d["disclaimer"]
    bad = client.post("/api/assessment/simulate-improvement", json={"answers": public_profile(), "fix_findings": ["NOPE"]})
    assert bad.status_code == 400


def test_core_endpoints(client):
    aid = post(client, public_profile()).get_json()["assessment_id"]
    assert client.get(f"/api/assessment/{aid}/recommendations").get_json()["recommendations"]
    assert len(client.get("/api/privacy-checklist").get_json()["items"]) == 18
    stats = client.get("/api/dashboard/stats").get_json()
    assert stats["cohort_size"] >= 1000 and "_scores" not in stats
    assert len(client.get("/api/questionnaire").get_json()["categories"]) == 10


def test_metadata_strip_removes_exif(client):
    import io
    from PIL import Image
    img = Image.new("RGB", (40, 30), "red"); ex = Image.Exif(); ex[271] = "FakeCam"; ex[306] = "2026:01:01 10:00:00"
    buf = io.BytesIO(); img.save(buf, "JPEG", exif=ex)
    ins = client.post("/api/metadata/inspect", data={"image": (io.BytesIO(buf.getvalue()), "a.jpg")}, content_type="multipart/form-data").get_json()
    assert ins["flags"]["has_device"] and ins["flags"]["has_timestamp"]
    out = client.post("/api/metadata/strip", data={"image": (io.BytesIO(buf.getvalue()), "a.jpg")}, content_type="multipart/form-data")
    clean = client.post("/api/metadata/inspect", data={"image": (io.BytesIO(out.data), "b.jpg")}, content_type="multipart/form-data").get_json()
    assert clean["field_count"] == 0
    assert client.post("/api/metadata/inspect", data={"image": (io.BytesIO(b"not an image"), "x.jpg")}, content_type="multipart/form-data").status_code == 400
