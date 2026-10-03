"""
FILE: data/generate_dataset.py
PURPOSE: Generate 1,200 FICTIONAL privacy-assessment records.
Run:  python data/generate_dataset.py          (from the project root)

* 100% synthetic - no real person, no scraping, no real accounts.
* Each profile has a hidden "awareness" level (0..1). Aware users tend to pick
  low-risk answers, careless users high-risk answers, so the data has realistic
  correlations (not uniform noise). A fixed seed makes it reproducible.
* Scores are computed with the SAME scoring engine as the app.
"""
import csv
import math
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.config import CATEGORY_KEYS  # noqa: E402
from backend.questionnaire import QUESTIONS  # noqa: E402
from backend.services.assessment_engine import score_answers  # noqa: E402

N_RECORDS = 1200
SEED = 42
OUT = ROOT / "data" / "social_media_privacy_assessments.csv"

# segment -> (mean awareness shift). Students overshare more; SMB owners less careful about settings.
SEGMENTS = {"Student": -0.08, "Job Seeker": 0.0, "Professional": 0.06, "SMB Owner": -0.02, "Educator": 0.05}
SEGMENT_WEIGHTS = [0.34, 0.2, 0.24, 0.12, 0.10]

# Per-question bias: positive = people more often pick the risky option.
BIAS = {"login_alerts_enabled": 0.18, "third_party_apps_reviewed": 0.2, "old_posts_reviewed": 0.2,
        "privacy_settings_reviewed": 0.12, "tag_review_enabled": 0.12, "unused_accounts": 0.15,
        "photo_metadata_awareness": 0.18, "phone_public": -0.12, "home_info_public": -0.25,
        "email_public": -0.08, "shares_verification_codes": -0.3, "mfa_enabled": 0.0,
        "password_manager_used": 0.1, "sessions_reviewed": 0.2, "profile_visibility": -0.05}

SPEC_COLUMNS = ["profile_visibility", "phone_public", "email_public", "birthday_public", "location_public",
                "workplace_public", "education_public", "relationship_public", "posts_public", "location_tagging",
                "travel_posts", "unknown_connections", "tag_review_enabled", "third_party_apps_reviewed",
                "mfa_enabled", "login_alerts_enabled", "password_reuse_reported", "suspicious_link_awareness",
                "old_posts_reviewed", "privacy_settings_reviewed"]


def pick(rng, q, target):
    options = q["options"]
    weights = []
    for o in options:
        w = math.exp(-((o["risk"] - target) ** 2) / 0.07)
        if o["value"] == "NOT_SURE":
            w *= 0.35  # unsure answers are rarer
        weights.append(w)
    return rng.choices([o["value"] for o in options], weights)[0]


def generate(n=N_RECORDS, seed=SEED):
    rng = random.Random(seed)
    today = date(2026, 9, 30)
    rows = []
    for i in range(1, n + 1):
        seg = rng.choices(list(SEGMENTS), SEGMENT_WEIGHTS)[0]
        day_offset = rng.randint(0, 364)
        # awareness improves slowly towards recent dates (a plausible training effect)
        recency_boost = 0.08 * (1 - day_offset / 364)
        awareness = min(0.98, max(0.02, rng.betavariate(2.6, 2.3) + SEGMENTS[seg] + recency_boost))
        answers = {}
        for q in QUESTIONS:
            target = min(1, max(0, (1 - awareness) + rng.gauss(0, 0.16) + BIAS.get(q["key"], 0)))
            answers[q["id"]] = pick(rng, q, target)
        # consistency rules
        if answers["G1"] == "NO":
            answers["G2"] = "NONE"
        elif answers["G2"] == "NONE":
            answers["G2"] = "SMS"
        res = score_answers(answers)
        row = {"profile_id": f"SYN-{i:05d}", "segment": seg,
               "assessment_date": (today - timedelta(days=day_offset)).isoformat()}
        for q in QUESTIONS:
            row[q["key"]] = answers[q["id"]]
        for c in CATEGORY_KEYS:
            row[f"score_{c}"] = round(res["category_scores"][c], 1)
        row["risk_score"] = res["overall_score"]
        row["risk_level"] = res["risk_level"]
        rows.append(row)
    return rows


def main():
    rows = generate()
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    levels = {}
    for r in rows:
        levels[r["risk_level"]] = levels.get(r["risk_level"], 0) + 1
    print(f"Wrote {len(rows)} synthetic records -> {OUT}")
    print("Risk level distribution:", levels)


if __name__ == "__main__":
    main()
