"""
FILE: backend/services/recommendation_engine.py
PURPOSE: generate_recommendations() - personalised actions, prioritised
IMMEDIATE -> IMPORTANT -> GOOD PRACTICE (ties broken by points saved).
"""
from ..knowledge_base import KB, PRIORITY_ORDER


def generate_recommendations(findings: list) -> list:
    recs = []
    for f in findings:
        t = KB[f["finding_type"]]
        recs.append({
            "finding_type": f["finding_type"],
            "category": f["category"],
            "risk": t[0],
            "recommendation": t[2],
            "priority": t[3],
            "points_saved": f.get("impact_points", 0),
        })
    recs.sort(key=lambda r: (PRIORITY_ORDER[r["priority"]], -r["points_saved"]))
    return recs
