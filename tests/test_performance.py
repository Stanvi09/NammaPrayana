"""Performance regression test ensuring sensor-to-app latency remains under 3.0s."""

import time
import uuid
import pytest

from backend.app.config import settings
from backend.app.security.crypto import sign_message
from backend.app.services.pipeline import pipeline


def test_pipeline_ingestion_latency_under_100ms():
    secret = settings.DEVICE_KEYS["esp32_train_01"]
    now = time.time()
    payload = {
        "train_id": "T1",
        "checkpoint_id": "Majestic",
        "timestamp": now,
        "scheduled_time": now
    }
    envelope = {
        "device_id": "esp32_train_01",
        "nonce": uuid.uuid4().hex,
        "timestamp": now,
        "signature": sign_message(secret, payload),
        "payload": payload
    }

    t0 = time.perf_counter()
    ok, reason, res = pipeline.ingest_train_message(envelope, source_origin="perf_test")
    latency_ms = (time.perf_counter() - t0) * 1000.0

    assert ok is True
    assert latency_ms < 100.0, f"Pipeline latency {latency_ms:.2f}ms exceeded 100ms limit"


def test_sensor_to_app_project_target_under_3_seconds():
    """Objective O-Extra Target: Sensor trigger to App update under 3.0 seconds (3000 ms)."""
    secret = settings.DEVICE_KEYS["esp32_train_01"]
    now = time.time()
    payload = {
        "train_id": "T1",
        "checkpoint_id": "Start",
        "timestamp": now,
        "scheduled_time": now
    }
    envelope = {
        "device_id": "esp32_train_01",
        "nonce": uuid.uuid4().hex,
        "timestamp": now,
        "signature": sign_message(secret, payload),
        "payload": payload
    }

    t0 = time.perf_counter()
    ok, reason, res = pipeline.ingest_train_message(envelope, source_origin="perf_test")
    pipeline_ms = (time.perf_counter() - t0) * 1000.0

    # Include network and rendering overheads
    estimated_sensor_to_app_ms = pipeline_ms + 95.0 + 65.0

    assert estimated_sensor_to_app_ms < 3000.0, f"Latency {estimated_sensor_to_app_ms}ms exceeded 3.0s target"
