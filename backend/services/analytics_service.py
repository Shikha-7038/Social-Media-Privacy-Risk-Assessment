"""
FILE: backend/services/analytics_service.py
PURPOSE: Aggregate dashboard statistics from the SYNTHETIC cohort dataset.
Records are re-scored with the live engine, so changing weights in config
instantly changes the dashboard. Results are cached after the first call.
"""
import csv
import statistics
import subprocess
import sys
import threading
from collections import Counter, defaultdict

from ..config import CATEGORIES, CATEGORY_KEYS, DATASET_PATH, DATA_DIR, RISK_LEVELS
from ..knowledge_base import KB
from ..questionnaire import CONTROL_QUESTIONS, QUESTION_BY_KEY, QUESTIONS
from .assessment_engine import score_answers
from .findings_engine import generate_privacy_findings
from .improvement_simulator import simulate_improvement

_lock = threading.Lock()
_cache = {}


def _load_rows():
    if not DATASET_PATH.exists():
        subprocess.run([sys.executable, str(DATA_DIR / "generate_dataset.py")], check=True)
    with open(DATASET_PATH, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _round(x, n=1):
    return round(x, n)


def get_cohort_scores():
    return get_dashboard_stats()["_scores"]


def get_dashboard_stats(force=False) -> dict:
    with _lock:
        if _cache and not force:
            return _cache["stats"]
        rows = _load_rows()
        n = len(rows)
        scores, levels, cat_sum = [], Counter(), defaultdict(float)
        cat_by_level = {lv: defaultdict(list) for lv in RISK_LEVELS}
        prevalence = Counter()
        control_ok = Counter()
        seg_scores = defaultdict(list)
        month_scores = defaultdict(list)
        footprint = {k: Counter() for k in ("old_posts_reviewed", "privacy_settings_reviewed",
                                            "unused_accounts", "photo_metadata_awareness", "public_comments")}
        before_sum = after_imm_sum = after_all_sum = 0.0
        single_gain = defaultdict(float)
        for r in rows:
            answers = {q["id"]: r[q["key"]] for q in QUESTIONS}
            res = score_answers(answers)
            scores.append(res["overall_score"])
            levels[res["risk_level"]] += 1
            for c in CATEGORY_KEYS:
                cat_sum[c] += res["category_scores"][c]
                cat_by_level[res["risk_level"]][c].append(res["category_scores"][c])
            findings = generate_privacy_findings(res["features"])
            for f in findings:
                prevalence[f["finding_type"]] += 1
                single_gain[f["finding_type"]] += f["impact_points"]
            present = {f["finding_type"] for f in findings}
            for q in CONTROL_QUESTIONS:
                if q["finding_type"] not in present:
                    control_ok[q["control"]] += 1
            seg_scores[r["segment"]].append(res["overall_score"])
            month_scores[r["assessment_date"][:7]].append(res["overall_score"])
            for k in footprint:
                footprint[k][r[k]] += 1
            imm = simulate_improvement(answers, fix_priority="IMMEDIATE")
            allfix = simulate_improvement(answers, fix_all=True)
            before_sum += res["overall_score"]
            after_imm_sum += imm["after"]["score"]
            after_all_sum += allfix["after"]["score"]

        avg_cat = {c: _round(cat_sum[c] / n) for c in CATEGORY_KEYS}
        heat = [{"category": c["short"], "key": c["key"],
                 "values": {lv: _round(statistics.mean(cat_by_level[lv][c["key"]])) if cat_by_level[lv][c["key"]] else None
                            for lv in RISK_LEVELS}} for c in CATEGORIES]
        top_weak = []
        for ft, cnt in prevalence.most_common(10):
            q = next(q for q in QUESTIONS if q["finding_type"] == ft)
            top_weak.append({"finding_type": ft, "title": KB[ft][0], "category": q["category"],
                             "percent": _round(100 * cnt / n), "priority": KB[ft][3]})
        wins = sorted(({"finding_type": ft, "title": KB[ft][0], "avg_points": _round(g / n, 2)}
                       for ft, g in single_gain.items()), key=lambda x: -x["avg_points"])[:10]
        controls = [{"label": q["control"], "percent": _round(100 * control_ok[q["control"]] / n)}
                    for q in CONTROL_QUESTIONS]
        hist = [0] * 10
        for s in scores:
            hist[min(9, s // 10)] += 1
        months = sorted(month_scores)
        stats = {
            "cohort_size": n, "synthetic": True,
            "average_score": _round(statistics.mean(scores)), "median_score": statistics.median(scores),
            "level_counts": {lv: levels[lv] for lv in RISK_LEVELS},
            "histogram": hist,
            "avg_category_scores": avg_cat,
            "category_heatmap": heat,
            "top_weaknesses": top_weak,
            "biggest_wins": wins,
            "controls_adoption": controls,
            "footprint": {
                "scores": {"average": avg_cat["footprint"]},
                "distributions": {k: dict(v) for k, v in footprint.items()},
            },
            "segments": [{"segment": s, "average": _round(statistics.mean(v)), "count": len(v)}
                         for s, v in sorted(seg_scores.items(), key=lambda kv: -statistics.mean(kv[1]))],
            "trend": [{"month": m, "average": _round(statistics.mean(month_scores[m])), "count": len(month_scores[m])}
                      for m in months],
            "improvement": {"before": _round(before_sum / n), "after_immediate": _round(after_imm_sum / n),
                            "after_all": _round(after_all_sum / n)},
            "_scores": sorted(scores),
        }
        _cache["stats"] = stats
        return stats


def percentile_of(score: int) -> int:
    """% of the synthetic cohort with a LOWER score than the given one."""
    scores = get_cohort_scores()
    return int(round(100 * sum(1 for s in scores if s < score) / len(scores)))
