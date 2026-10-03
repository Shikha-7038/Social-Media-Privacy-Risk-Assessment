"""Shared pytest fixtures: every test run uses a throw-away database."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app import create_app  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    return create_app({"DATABASE_PATH": str(tmp_path / "test.db"), "RATE_LIMIT": 10_000, "WRITE_RATE_LIMIT": 10_000})


@pytest.fixture()
def client(app):
    return app.test_client()
