"""Tests for crowd prediction model, baseline comparison, and 80% ground-truth target."""

import csv
import pytest
from backend.app.config import BASE_DIR
from backend.app.crowd.model import crowd_model, StationAverageBaseline
from backend.app.services.crowd_engine import crowd_engine

HAND_COUNTS_FILE = BASE_DIR / "data" / "hand_counts.csv"


def test_crowd_model_prediction_levels():
    # Low crowd scenario (off-peak, low occupancy, far from stairs)
    low_pred = crowd_model.predict(people_count=12, time_of_day_hour=14.0, coach_position=6)
    assert low_pred == "Low"

    # High crowd scenario (rush hour, high occupancy, adjacent to stairs)
    high_pred = crowd_model.predict(people_count=65, time_of_day_hour=9.0, coach_position=2)
    assert high_pred == "High"


def test_crowd_model_matches_ground_truth_target():
    """Objective O2 Target: >= 80% agreement with hand-count ground truth."""
    if not HAND_COUNTS_FILE.exists():
        pytest.skip("hand_counts.csv not present, run train.py first")

    rows = []
    with open(HAND_COUNTS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    assert len(rows) >= 60, "Dataset must contain at least 60 crowd instances"

    matches = 0
    baseline_matches = 0
    baseline = StationAverageBaseline()

    for r in rows:
        cnt = int(float(r["people_count"]))
        hour = float(r["hour"])
        coach_pos = int(float(r["coach_position"]))
        ground_truth = r["ground_truth_label"]

        pred = crowd_model.predict(cnt, hour, coach_pos)
        base_pred = baseline.predict(cnt, hour)

        if pred == ground_truth:
            matches += 1
        if base_pred == ground_truth:
            baseline_matches += 1

    accuracy = (matches / len(rows)) * 100.0
    baseline_acc = (baseline_matches / len(rows)) * 100.0

    print(f"\nCrowd Model Accuracy against Hand Counts: {accuracy:.2f}% (Baseline: {baseline_acc:.2f}%)")
    assert accuracy >= 80.0, f"Crowd model accuracy {accuracy:.2f}% fell below 80% target!"


def test_simulated_coaches_distinguished_from_real():
    summary = crowd_engine.get_train_crowd_summary("T1")
    assert summary["real_sensor_coach"] == "C1"
    assert "C2" in summary["simulated_coaches"]

    for coach in summary["coaches"]:
        if coach["coach_id"] == "C1":
            assert coach["is_simulated"] is False
        else:
            assert coach["is_simulated"] is True
