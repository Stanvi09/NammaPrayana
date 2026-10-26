"""Pytest configuration and common fixtures for NammaFlow."""

import os
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.database import Database
from backend.app.security.replay import replay_detector


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Sets up an isolated test database and resets replay protection cache."""
    test_db_path = tmp_path / "test_nammaflow.db"
    settings.DB_PATH = test_db_path
    settings.MQTT_ENABLED = False
    settings.REQUIRE_SIGNATURES = True

    # Re-initialize DB
    from backend.app.database import db
    db.db_path = test_db_path
    db._init_db()

    # Reset replay cache
    replay_detector.reset()

    yield

    replay_detector.reset()
