"""Runs every documented test case (T01-T30) plus extra scoring checks."""
import pytest

from backend.config import CATEGORY_KEYS, get_category_weights
from backend.questionnaire import QUESTIONS
from backend.services.scoring_engine import calculate_privacy_risk

from .test_cases import CASES


@pytest.mark.parametrize("c", CASES, ids=[c["id"] for c in CASES])
def test_documented_case(c):
    ok, actual = c["run"]()
    assert ok, f"{c['id']} {c['scenario']}: {actual}"


def test_at_least_40_questions():
    assert len(QUESTIONS) >= 40


def test_default_weights_sum_to_100():
    assert sum(get_category_weights().values()) == 100


def test_weights_configurable():
    cats = {k: 0.0 for k in CATEGORY_KEYS}; cats["account_security"] = 100.0
    default = calculate_privacy_risk(cats)["overall_score"]
    heavy = calculate_privacy_risk(cats, {**get_category_weights(), "account_security": 45})["overall_score"]
    assert heavy > default


def test_higher_score_means_higher_risk():
    from .helpers import private_profile, public_profile, with_
    from backend.services.assessment_engine import score_answers
    base = score_answers(private_profile())["overall_score"]
    worse = score_answers(with_(private_profile(), phone_public="YES"))["overall_score"]
    assert worse > base and score_answers(public_profile())["overall_score"] > worse
