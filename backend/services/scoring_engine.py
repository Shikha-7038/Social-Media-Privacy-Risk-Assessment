"""
FILE: backend/services/scoring_engine.py
PURPOSE: Category-wise scoring and the overall privacy risk score.

Maths (simple and explainable):
    category_score = 100 * sum(weight_i * risk_i) / sum(weight_i)      (0-100)
    overall_score  = sum(category_weight_c * category_score_c) / sum(category_weight_c)

0 = lower assessed risk, 100 = higher assessed risk. Because the model is linear,
each answer contributes an exact number of "points" to the overall score
(see feature_points), which makes findings and the simulator explainable.

NOTE: weights/thresholds are EDUCATIONAL ASSUMPTIONS - validate before real use.
"""
from ..config import CATEGORY_KEYS, RISK_BANDS, get_category_weights


def classify_risk(score) -> str:
    """0-20 LOW, 21-40 MODERATE, 41-70 HIGH, 71-100 CRITICAL (score rounded to int)."""
    s = int(round(score))
    for upper, label in RISK_BANDS:
        if s <= upper:
            return label
    return RISK_BANDS[-1][1]


def _category_totals(features):
    totals = {c: [0.0, 0.0] for c in CATEGORY_KEYS}  # [weighted risk, weight]
    for f in features.values():
        totals[f["category"]][0] += f["weight"] * f["risk"]
        totals[f["category"]][1] += f["weight"]
    return totals


def calculate_category_scores(features: dict) -> dict:
    """Return {category_key: score 0-100 (float)} from extracted features."""
    totals = _category_totals(features)
    return {c: (100.0 * w_risk / w if w else 0.0) for c, (w_risk, w) in totals.items()}


def calculate_privacy_risk(category_scores: dict, weights: dict = None) -> dict:
    """Combine category scores with configurable weights -> overall score + level."""
    weights = weights or get_category_weights()
    total_w = sum(weights[c] for c in CATEGORY_KEYS)
    overall = sum(weights[c] * category_scores.get(c, 0.0) for c in CATEGORY_KEYS) / total_w
    overall = max(0.0, min(100.0, overall))
    return {"overall_score": int(round(overall)), "overall_exact": overall,
            "risk_level": classify_risk(overall)}


def feature_points(features: dict, weights: dict = None) -> dict:
    """Exact points each feature adds to the overall score: {key: points}."""
    weights = weights or get_category_weights()
    total_w = sum(weights[c] for c in CATEGORY_KEYS)
    totals = _category_totals(features)
    pts = {}
    for key, f in features.items():
        cat_w = totals[f["category"]][1]
        pts[key] = (weights[f["category"]] / total_w) * (f["weight"] * f["risk"] / cat_w) * 100.0 if cat_w else 0.0
    return pts
