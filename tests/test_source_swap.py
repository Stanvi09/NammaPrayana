"""Tests for Source-Swap architecture (recorded data flowing through same pipeline)."""

import json
from pathlib import Path
import pytest

from backend.app.config import BASE_DIR
from backend.app.database import db
from backend.app.services.source_swap import source_swap_adapter

SAMPLE_FILE = BASE_DIR / "data" / "recorded_sample.json"


def test_source_swap_ingestion_success():
    assert SAMPLE_FILE.exists()

    result = source_swap_adapter.ingest_file(SAMPLE_FILE)

    assert result["total_records"] == 4
    assert result["train_processed"] == 3
    assert result["door_processed"] == 1
    assert result["rejected_count"] == 0

    # Verify records in database
    latest_train = db.get_latest_train_event("T1")
    assert latest_train is not None
    assert latest_train["checkpoint_id"] == "Majestic"

    # Verify prediction generated
    latest_pred = db.get_latest_delay_prediction("T1")
    assert latest_pred is not None
    assert latest_pred["checkpoint_id"] == "Majestic"
