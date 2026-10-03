"""
FILE: backend/config.py
PURPOSE: Central configuration - paths, scoring weights, risk bands, limits.

Everything an instructor/employer might want to "tune" lives here, so the
scoring model is transparent and configurable (see README -> Risk Scoring).

IMPORTANT: weights and thresholds are EDUCATIONAL ASSUMPTIONS. They must be
validated and calibrated before being used for any professional risk decision.
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATASET_PATH = DATA_DIR / "social_media_privacy_assessments.csv"


def _load_env_file() -> None:
    """Tiny .env loader (avoids an extra dependency). Real env vars win."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


class Config:
    """Runtime settings read from environment variables (see .env.example)."""
    HOST = os.getenv("HOST", "127.0.0.1")          # localhost only by default
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "backend" / "privacy_assessments.db"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))        # all requests
    WRITE_RATE_LIMIT_PER_MINUTE = int(os.getenv("WRITE_RATE_LIMIT_PER_MINUTE", "20"))  # POST/DELETE
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))                       # auto-delete old assessments
    MAX_JSON_BYTES = 64 * 1024
    MAX_IMAGE_BYTES = 8 * 1024 * 1024
    MAX_CONTENT_LENGTH = 9 * 1024 * 1024


# ---------------------------------------------------------------------------
# The 10 scoring categories (letters A-J match the questionnaire sections)
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"key": "profile",            "letter": "A", "label": "Profile Visibility",       "short": "Profile",
     "blurb": "Who can find and view your profile."},
    {"key": "personal_info",      "letter": "B", "label": "Personal Information",     "short": "Personal Info",
     "blurb": "Contact, birthday, home, work and family details."},
    {"key": "location",           "letter": "C", "label": "Location Privacy",         "short": "Location",
     "blurb": "Live location, geotags, check-ins and travel posts."},
    {"key": "content",            "letter": "D", "label": "Posts & Content",          "short": "Content",
     "blurb": "Who sees your posts and what your photos reveal."},
    {"key": "connections",        "letter": "E", "label": "Friends / Followers",      "short": "Connections",
     "blurb": "Who can connect with you and how you vet them."},
    {"key": "tagging",            "letter": "F", "label": "Tagging & Mentions",       "short": "Tagging",
     "blurb": "What other people can post about you."},
    {"key": "account_security",   "letter": "G", "label": "Authentication & Account Security", "short": "Account Security",
     "blurb": "MFA, passwords, alerts and session hygiene."},
    {"key": "third_party",        "letter": "H", "label": "Third-Party Apps",         "short": "Third-Party Apps",
     "blurb": "Apps and sites connected to your account."},
    {"key": "social_engineering", "letter": "I", "label": "Messaging & Social Engineering", "short": "Social Engineering",
     "blurb": "How you handle scams, links and impersonation."},
    {"key": "footprint",          "letter": "J", "label": "Digital Footprint",        "short": "Digital Footprint",
     "blurb": "Old posts, old accounts and review habits."},
]
CATEGORY_KEYS = [c["key"] for c in CATEGORIES]
CATEGORY_LABELS = {c["key"]: c["label"] for c in CATEGORIES}
CATEGORY_SHORT = {c["key"]: c["short"] for c in CATEGORIES}

# Default weights from the project brief (sum = 100).
DEFAULT_CATEGORY_WEIGHTS = {
    "profile": 10, "personal_info": 15, "location": 15, "content": 10,
    "connections": 10, "tagging": 5, "account_security": 15,
    "third_party": 5, "social_engineering": 10, "footprint": 5,
}

# Risk bands: (upper bound inclusive, label). Higher score = HIGHER exposure.
RISK_BANDS = [(20, "LOW"), (40, "MODERATE"), (70, "HIGH"), (100, "CRITICAL")]
RISK_LEVELS = [b[1] for b in RISK_BANDS]

# A finding is raised when a question's risk value is at or above this.
FINDING_THRESHOLD = 0.5
# A category is "high-risk" when its score is at or above this (HIGH band start).
HIGH_RISK_CATEGORY_SCORE = 41

DISCLAIMER = (
    "This is an educational privacy-risk framework based on self-reported answers. "
    "It is not a guarantee that an account will or will not be compromised, and its "
    "weights and thresholds are educational assumptions that should be validated "
    "before any professional risk decision."
)


def get_category_weights() -> dict:
    """Return category weights, optionally overridden by CATEGORY_WEIGHTS_JSON.

    Example: CATEGORY_WEIGHTS_JSON='{"account_security": 25, "tagging": 2}'
    Unknown keys / non-positive numbers are ignored. Weights are used as
    ratios, so they do not have to sum to exactly 100.
    """
    weights = dict(DEFAULT_CATEGORY_WEIGHTS)
    raw = os.getenv("CATEGORY_WEIGHTS_JSON")
    if raw:
        try:
            override = json.loads(raw)
            for k, v in override.items():
                if k in weights and isinstance(v, (int, float)) and v > 0:
                    weights[k] = float(v)
        except (ValueError, AttributeError):
            pass  # bad JSON -> fall back to defaults
    return weights
