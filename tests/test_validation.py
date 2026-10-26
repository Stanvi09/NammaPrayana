"""Tests for watchdog silent sensor detection and data bounds."""

import time
import pytest
from backend.app.database import db
from backend.app.services.watchdog import SensorWatchdog


def test_sensor_watchdog_detects_silent_sensor():
    watchdog = SensorWatchdog(timeout_seconds=5.0)
    now = 1000.0

    # Device checks in at t=1000
    watchdog.record_activity("esp32_train_01", timestamp=now)

    # At t=1003, device is still within timeout (3s < 5s)
    alerts = watchdog.check_silent_sensors(current_time=1003.0)
    assert not any(a["device_id"] == "esp32_train_01" for a in alerts)

    # At t=1008, device has been silent for 8s > 5s threshold -> alert raised!
    alerts = watchdog.check_silent_sensors(current_time=1008.0)
    train_alerts = [a for a in alerts if a["device_id"] == "esp32_train_01"]
    assert len(train_alerts) == 1
    assert train_alerts[0]["status"] == "SILENT_SENSOR_ALERT"
    assert "went silent" in train_alerts[0]["message"]
