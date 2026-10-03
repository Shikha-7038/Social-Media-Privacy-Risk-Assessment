"""
FILE: backend/routes/api.py
PURPOSE: REST API.

Authentication/authorisation: the app has no user accounts (data minimisation).
An assessment id is an unguessable random capability token (48 bits of
randomness): only someone holding it can read, report on or delete the record.
"""
from flask import Blueprint, Response, current_app, jsonify, request

from ..config import Config, DISCLAIMER
from ..knowledge_base import AWARENESS_TIPS, CHECKLIST
from ..models import database as db
from ..questionnaire import public_questionnaire
from ..services import analytics_service, metadata_service
from ..services.assessment_engine import build_view, run_assessment
from ..services.demo_profile import DEMO_IMPROVEMENTS, demo_answers
from ..services.improvement_simulator import SimulationError, simulate_improvement
from ..services.report_service import generate_report_html
from ..utils.security import apply_security_headers
from ..utils.validators import ValidationError, validate_answers, validate_assessment_id

api = Blueprint("api", __name__, url_prefix="/api")


def _db():
    return current_app.config["DATABASE_PATH"]


def _json_body():
    if request.content_length and request.content_length > Config.MAX_JSON_BYTES:
        raise ValidationError("Request body too large.")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Body must be a JSON object.")
    return data


def _view_from_db(aid):
    raw = db.load_assessment(aid, _db())
    if raw is None:
        return None
    view = build_view(raw["overall_score"], raw["risk_level"], raw["category_scores"], raw["findings"])
    view.update(assessment_id=raw["assessment_id"], created_at=raw["created_at"],
                percentile=analytics_service.percentile_of(raw["overall_score"]))
    return view


@api.errorhandler(ValidationError)
def _bad(err):
    return jsonify({"error": "validation_error", "details": err.errors}), 400


@api.errorhandler(SimulationError)
def _bad_sim(err):
    return jsonify({"error": "validation_error", "details": [str(err)]}), 400


@api.errorhandler(metadata_service.ImageError)
def _bad_img(err):
    return jsonify({"error": "invalid_image", "details": [str(err)]}), 400


@api.get("/health")
def health():
    return jsonify({"status": "ok", "synthetic_cohort": True})


@api.get("/questionnaire")
def questionnaire():
    return jsonify(public_questionnaire())


@api.post("/assessment")
def create_assessment():
    answers = validate_answers(_json_body().get("answers"))
    view = run_assessment(answers)           # answers are used here and then discarded
    meta = db.save_assessment(view, _db())   # only scores + finding types are stored
    view.update(meta, percentile=analytics_service.percentile_of(view["overall_score"]))
    return jsonify(view), 201


@api.get("/assessment/<aid>")
def get_assessment(aid):
    validate_assessment_id(aid)
    view = _view_from_db(aid)
    if view is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(view)


@api.get("/assessment/<aid>/recommendations")
def get_recommendations(aid):
    validate_assessment_id(aid)
    view = _view_from_db(aid)
    if view is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"assessment_id": aid, "recommendations": view["recommendations"],
                    "counts": view["recommendation_counts"], "awareness_tips": AWARENESS_TIPS})


@api.get("/assessment/<aid>/report")
def get_report(aid):
    validate_assessment_id(aid)
    view = _view_from_db(aid)
    if view is None:
        return jsonify({"error": "not_found"}), 404
    resp = Response(generate_report_html(view), mimetype="text/html")
    if request.args.get("download") == "1":
        resp.headers["Content-Disposition"] = f'attachment; filename="privacy-report-{aid}.html"'
    return apply_security_headers(resp, is_report=True)


@api.delete("/assessment/<aid>")
def delete_assessment(aid):
    validate_assessment_id(aid)
    if not db.delete_assessment(aid, _db()):
        return jsonify({"error": "not_found"}), 404
    return jsonify({"deleted": True, "assessment_id": aid})


@api.post("/assessment/simulate-improvement")
def simulate():
    body = _json_body()
    answers = validate_answers(body.get("answers"))
    changes = body.get("changes") or {}
    fixes = body.get("fix_findings") or []
    if not isinstance(changes, dict) or not isinstance(fixes, list) or len(fixes) > 60 or len(changes) > 60:
        raise ValidationError("'changes' must be an object and 'fix_findings' a short list.")
    if not all(isinstance(f, str) and len(f) < 60 for f in fixes):
        raise ValidationError("'fix_findings' must be a list of strings.")
    prio = body.get("fix_priority")
    if prio is not None and prio not in ("IMMEDIATE", "IMPORTANT", "GOOD PRACTICE"):
        raise ValidationError("Invalid fix_priority.")
    return jsonify(simulate_improvement(answers, changes=changes, fix_findings=fixes,
                                        fix_priority=prio, fix_all=body.get("fix_all") is True))


@api.get("/dashboard/stats")
def dashboard_stats():
    stats = {k: v for k, v in analytics_service.get_dashboard_stats().items() if not k.startswith("_")}
    stats["live"] = db.live_stats(_db())
    stats["tips"] = AWARENESS_TIPS
    return jsonify(stats)


@api.get("/privacy-checklist")
def checklist():
    return jsonify({"title": "Social Media Privacy Checklist",
                    "items": [{"id": i, "text": t, "category": c} for i, (t, c) in enumerate(CHECKLIST, 1)],
                    "disclaimer": DISCLAIMER})


@api.get("/demo")
def demo():
    """Fictional demo profile: scored on the fly, NOT stored."""
    answers = demo_answers()
    view = run_assessment(answers)
    sim = simulate_improvement(answers, changes=DEMO_IMPROVEMENTS)
    imm = simulate_improvement(answers, fix_priority="IMMEDIATE")
    view.update(assessment_id="DEMO-FICTIONAL", created_at="synthetic demo profile", demo=True,
                percentile=analytics_service.percentile_of(view["overall_score"]),
                answers=answers, brief_simulation=sim, immediate_simulation=imm)
    return jsonify(view)


@api.post("/metadata/inspect")
def metadata_inspect():
    f = request.files.get("image")
    if f is None:
        raise ValidationError("Attach an image in the 'image' field.")
    return jsonify(metadata_service.inspect_metadata(f.read(Config.MAX_IMAGE_BYTES + 1)))


@api.post("/metadata/strip")
def metadata_strip():
    f = request.files.get("image")
    if f is None:
        raise ValidationError("Attach an image in the 'image' field.")
    data, fmt = metadata_service.strip_metadata(f.read(Config.MAX_IMAGE_BYTES + 1))
    ext = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "TIFF": "tiff"}[fmt]
    resp = Response(data, mimetype=f"image/{fmt.lower()}")
    resp.headers["Content-Disposition"] = f'attachment; filename="cleaned-copy.{ext}"'
    return resp
