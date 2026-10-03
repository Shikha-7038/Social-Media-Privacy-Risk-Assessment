"""
FILE: backend/services/improvement_simulator.py
PURPOSE: "What happens if I improve my settings?"  Re-scores a COPY of the
answers with the chosen improvements applied. Nothing is stored.

Label every output as a framework simulation, not a guarantee of safety.
"""
from ..config import CATEGORIES, get_category_weights
from ..knowledge_base import KB
from ..questionnaire import QUESTION_BY_FINDING, QUESTIONS, resolve_question
from .assessment_engine import score_answers
from .scoring_engine import classify_risk

SIM_DISCLAIMER = ("Framework simulation only: this estimates how the educational score would change "
                  "if you applied these settings. It is not a guarantee of real-world safety.")


class SimulationError(ValueError):
    pass


def simulate_improvement(answers: dict, changes: dict = None, fix_findings=None,
                         fix_priority: str = None, fix_all: bool = False, weights: dict = None) -> dict:
    weights = weights or get_category_weights()
    before = score_answers(answers, weights)
    new_answers = dict(answers)
    applied = []

    def apply(q, new_value):
        old = new_answers[q["id"]]
        if old != new_value:
            new_answers[q["id"]] = new_value
            applied.append({"question_id": q["id"], "finding_type": q["finding_type"],
                            "title": KB[q["finding_type"]][0], "from": old, "to": new_value})

    # explicit per-question changes ({"phone_public": "NO"})
    for k, v in (changes or {}).items():
        q = resolve_question(k)
        if q is None or v not in q["risk_map"]:
            raise SimulationError("Unknown question or invalid option in 'changes'.")
        apply(q, v)
    # fix selected finding types -> best (lowest-risk) answer
    for ft in (fix_findings or []):
        q = QUESTION_BY_FINDING.get(ft)
        if q is None:
            raise SimulationError("Unknown finding type.")
        apply(q, q["best_answer"])
    # bulk options
    if fix_all or fix_priority:
        for q in QUESTIONS:
            if before["features"][q["key"]]["risk"] < 0.5:
                continue
            if fix_all or KB[q["finding_type"]][3] == fix_priority:
                apply(q, q["best_answer"])

    after = score_answers(new_answers, weights)
    deltas = [{"key": c["key"], "label": c["short"],
               "before": int(round(before["category_scores"][c["key"]])),
               "after": int(round(after["category_scores"][c["key"]]))} for c in CATEGORIES]
    return {
        "before": {"score": before["overall_score"], "level": before["risk_level"]},
        "after": {"score": after["overall_score"], "level": after["risk_level"]},
        "risk_reduction": before["overall_score"] - after["overall_score"],
        "category_changes": deltas,
        "applied_changes": applied,
        "disclaimer": SIM_DISCLAIMER,
    }
