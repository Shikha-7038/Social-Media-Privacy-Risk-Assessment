"""
FILE: backend/services/findings_engine.py
PURPOSE: generate_privacy_findings() - turn risky answers into ranked findings.
"""
from ..config import FINDING_THRESHOLD
from ..knowledge_base import KB
from .scoring_engine import feature_points

SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _severity(base: str, risk: float) -> str:
    """Strong risk keeps the base severity; borderline (<0.75) drops one level."""
    idx = SEVERITY_ORDER.index(base)
    if risk < 0.75 and idx > 0:
        idx -= 1
    return SEVERITY_ORDER[idx]


def generate_privacy_findings(features: dict, weights: dict = None) -> list:
    """Return findings sorted by impact (points added to the overall score)."""
    points = feature_points(features, weights)
    findings = []
    for key, f in features.items():
        if f["risk"] >= FINDING_THRESHOLD:
            ftype = f["finding_type"]
            findings.append({
                "finding_type": ftype,
                "category": f["category"],
                "severity": _severity(f["severity"], f["risk"]),
                "title": KB[ftype][0],
                "description": KB[ftype][1],
                "impact_points": round(points[key], 2),
            })
    findings.sort(key=lambda x: (-x["impact_points"], x["finding_type"]))
    return findings
