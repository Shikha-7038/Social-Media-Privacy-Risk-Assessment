"""
FILE: backend/utils/validators.py
PURPOSE: Strict input validation (allow-list) for questionnaire answers.

Only known question ids and known answer codes are accepted. Anything else is
rejected, so no free text ever reaches the scoring engine, database or report.
Error messages never echo the submitted value (prevents reflected injection).
"""
import re
from ..questionnaire import QUESTIONS, resolve_question

ID_RE = re.compile(r"^[A-Za-z0-9-]{8,40}$")


class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("validation failed")
        self.errors = errors if isinstance(errors, list) else [errors]


def validate_assessment_id(value) -> str:
    if not isinstance(value, str) or not ID_RE.match(value):
        raise ValidationError("Invalid assessment id format.")
    return value


def validate_answers(payload, require_complete=True) -> dict:
    """Return {question_id: ANSWER_CODE} or raise ValidationError."""
    if not isinstance(payload, dict):
        raise ValidationError("'answers' must be an object of question-id -> answer.")
    if len(payload) > len(QUESTIONS):
        raise ValidationError("Too many answers supplied.")
    cleaned, errors = {}, []
    for raw_key, raw_val in payload.items():
        q = resolve_question(raw_key) if isinstance(raw_key, str) and len(raw_key) <= 40 else None
        if q is None:
            errors.append("Unknown question identifier.")
            continue
        if not isinstance(raw_val, str) or len(raw_val) > 30:
            errors.append(f"{q['id']}: answer must be a short string.")
            continue
        val = raw_val.strip().upper()
        if val not in q["risk_map"]:
            errors.append(f"{q['id']}: invalid answer option.")
            continue
        cleaned[q["id"]] = val
    if require_complete:
        missing = [q["id"] for q in QUESTIONS if q["id"] not in cleaned]
        if missing and not errors:
            errors.append("Missing answers for: " + ", ".join(missing))
    if errors:
        raise ValidationError(errors[:10])
    return cleaned
