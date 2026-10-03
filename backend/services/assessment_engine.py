"""
FILE: backend/services/assessment_engine.py
PURPOSE: Orchestrates the pipeline
  validated answers -> feature extraction -> category scores -> overall score
  -> findings -> recommendations -> dashboard-ready "view".
"""
from ..config import (CATEGORIES, CATEGORY_KEYS, DISCLAIMER, HIGH_RISK_CATEGORY_SCORE,
                      get_category_weights)
from ..knowledge_base import KB, PRIORITY_ORDER
from ..questionnaire import CONTROL_QUESTIONS, QUESTIONS
from .findings_engine import generate_privacy_findings
from .recommendation_engine import generate_recommendations
from .scoring_engine import calculate_category_scores, calculate_privacy_risk, classify_risk


def extract_privacy_features(answers: dict) -> dict:
    """Convert answers into numeric risk features.

    Returns {question_key: {answer, risk (0-1), weight, category, finding_type,
    severity, control}} - e.g. a public phone number becomes a high exposure
    contribution, MFA disabled an account-security contribution, etc.
    """
    features = {}
    for q in QUESTIONS:
        ans = answers[q["id"]]
        features[q["key"]] = {
            "question_id": q["id"], "answer": ans, "risk": q["risk_map"][ans],
            "weight": q["weight"], "category": q["category"],
            "finding_type": q["finding_type"], "severity": q["severity"],
            "control": q["control"],
        }
    return features


def score_answers(answers: dict, weights: dict = None) -> dict:
    """Pure scoring (no findings text) - used by simulator and analytics."""
    weights = weights or get_category_weights()
    features = extract_privacy_features(answers)
    cats = calculate_category_scores(features)
    overall = calculate_privacy_risk(cats, weights)
    return {"features": features, "category_scores": cats, **overall}


def build_view(overall_score, risk_level, category_scores, findings) -> dict:
    """Assemble the response/report shape from stored data only (no raw answers)."""
    cats = []
    for c in CATEGORIES:
        s = int(round(category_scores[c["key"]]))
        cats.append({"key": c["key"], "label": c["label"], "short": c["short"],
                     "score": s, "level": classify_risk(s)})
    recs = generate_recommendations(findings)
    present = {f["finding_type"] for f in findings}
    controls = [{"label": q["control"], "enabled": q["finding_type"] not in present,
                 "finding_type": q["finding_type"]} for q in CONTROL_QUESTIONS]
    by_prio = {p: sum(1 for r in recs if r["priority"] == p) for p in PRIORITY_ORDER}
    return {
        "overall_score": overall_score, "risk_level": risk_level,
        "category_scores": cats, "findings": findings, "recommendations": recs,
        "top_risks": [f["title"] for f in findings[:5]],
        "high_risk_categories": [c["short"] for c in cats if c["score"] >= HIGH_RISK_CATEGORY_SCORE],
        "controls": controls,
        "controls_enabled": sum(1 for c in controls if c["enabled"]),
        "controls_total": len(controls),
        "recommendation_counts": by_prio,
        "potential_reduction": int(round(sum(f["impact_points"] for f in findings
                                             if KB[f["finding_type"]][3] == "IMMEDIATE"))),
        "disclaimer": DISCLAIMER,
    }


def run_assessment(answers: dict, weights: dict = None) -> dict:
    """Full pipeline for validated answers."""
    scored = score_answers(answers, weights)
    findings = generate_privacy_findings(scored["features"], weights)
    cat_scores = {k: v for k, v in scored["category_scores"].items()}
    return build_view(scored["overall_score"], scored["risk_level"], cat_scores, findings)
