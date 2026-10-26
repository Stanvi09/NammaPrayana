"""Tests for all REST API endpoints."""

import time
import uuid
import pytest

from backend.app.config import settings
from backend.app.database import db
from backend.app.api.train import get_latest_train_status, ingest_train_checkpoint
from backend.app.api.delay import get_delay_prediction
from backend.app.api.crowd import get_crowd_status, ingest_door_count
from backend.app.api.context import get_current_context, update_demo_context_switch
from backend.app.api.security import get_security_audit_events, get_registered_devices
from backend.app.main import health_check
from backend.app.schemas.api_models import DemoSwitchRequest
from backend.app.security.crypto import sign_message


def test_health_endpoint():
    res = health_check()
    assert res.status in ["healthy", "degraded"]
    assert res.database == "connected"
    assert res.registered_devices_count >= 3


def test_train_latest_endpoint_standby_and_active():
    # 1. Standby
    standby = get_latest_train_status("T_TEST")
    assert standby.train_id == "T_TEST"
    assert "standby" in standby.status

    # 2. Ingest event
    now = time.time()
    secret = settings.DEVICE_KEYS["esp32_train_01"]
    payload = {"train_id": "T1", "checkpoint_id": "Start", "timestamp": now, "scheduled_time": now}
    msg = {
        "device_id": "esp32_train_01",
        "nonce": uuid.uuid4().hex,
        "timestamp": now,
        "signature": sign_message(secret, payload),
        "payload": payload
    }
    ingest_train_checkpoint(msg)

    # 3. Active status
    active = get_latest_train_status("T1")
    assert active.train_id == "T1"
    assert active.status == "in_transit"


def test_delay_prediction_endpoint():
    res = get_delay_prediction("T1")
    assert res.train_id == "T1"
    assert res.confidence_percentage > 50.0
    assert "minutes" in res.delay_range_text


def test_crowd_endpoint():
    res = get_crowd_status("T1")
    assert res["train_id"] == "T1"
    assert len(res["coaches"]) == 6
    assert res["real_sensor_coach"] == "C1"
    assert res["best_coach"] in ["C1", "C2", "C3", "C4", "C5", "C6"]


def test_context_and_demo_switch():
    ctx = get_current_context()
    assert "probable_factor" in ctx

    # Test demo switch toggle
    req = DemoSwitchRequest(rain=True, festival=False)
    update_res = update_demo_context_switch(req)
    assert update_res["current_context"]["rain"] is True

    # Reset
    reset_req = DemoSwitchRequest(reset_to_real=True)
    update_demo_context_switch(reset_req)


def test_security_audit_endpoints():
    events = get_security_audit_events(limit=10)
    assert "events" in events

    devices = get_registered_devices()
    assert devices["count"] >= 3
