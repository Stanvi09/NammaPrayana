"""Watchdog service to monitor sensor heartbeats and raise silent sensor alerts."""

import time
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.database import db
from backend.app.utils.logger import logger


class SensorWatchdog:
    """Detects missing sensor telemetry / silent hardware dropouts."""

    def __init__(self, timeout_seconds: Optional[float] = None):
        self.timeout_seconds = timeout_seconds or settings.SENSOR_SILENT_ALERT_SECONDS
        self._last_heartbeat: Dict[str, float] = {}

    def record_activity(self, device_id: str, timestamp: Optional[float] = None):
        """Records telemetry arrival from a sensor."""
        ts = timestamp if timestamp is not None else time.time()
        self._last_heartbeat[device_id] = ts
        db.update_device_seen(device_id)

    def check_silent_sensors(self, current_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """Scans all registered devices and returns alerts for any silent sensors."""
        now = current_time if current_time is not None else time.time()
        alerts = []

        devices = db.get_devices()
        for dev in devices:
            dev_id = dev["device_id"]
            if not dev["is_active"]:
                continue

            last_seen = self._last_heartbeat.get(dev_id, dev["last_seen"])
            if last_seen is None:
                # Device never checked in
                silence_duration = now - dev["created_at"]
                if silence_duration > self.timeout_seconds:
                    alert = {
                        "device_id": dev_id,
                        "device_type": dev["device_type"],
                        "status": "OFFLINE_NEVER_CONNECTED",
                        "silence_seconds": round(silence_duration, 1),
                        "message": f"Sensor '{dev_id}' has never reported telemetry since system startup"
                    }
                    alerts.append(alert)
            else:
                silence_duration = now - last_seen
                if silence_duration > self.timeout_seconds:
                    alert = {
                        "device_id": dev_id,
                        "device_type": dev["device_type"],
                        "status": "SILENT_SENSOR_ALERT",
                        "silence_seconds": round(silence_duration, 1),
                        "message": f"Sensor '{dev_id}' went silent: no message received for {int(silence_duration)}s (threshold: {int(self.timeout_seconds)}s)"
                    }
                    alerts.append(alert)
                    logger.warning(alert["message"])

        return alerts


sensor_watchdog = SensorWatchdog()
