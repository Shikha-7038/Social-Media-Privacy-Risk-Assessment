"""Helpers that build questionnaire answer sets for tests."""
from backend.questionnaire import QUESTION_BY_KEY, QUESTIONS


def private_profile() -> dict:
    """Every answer set to its lowest-risk option."""
    return {q["id"]: q["best_answer"] for q in QUESTIONS}


def public_profile() -> dict:
    """Every answer set to its highest-risk option."""
    return {q["id"]: q["worst_answer"] for q in QUESTIONS}


def with_(base: dict, **by_key) -> dict:
    """Copy `base` and override answers by question KEY, e.g. with_(p, phone_public='YES')."""
    out = dict(base)
    for key, value in by_key.items():
        out[QUESTION_BY_KEY[key]["id"]] = value
    return out
