"""Mosquitto MQTT client manager with reconnect handling and optional TLS."""

import ssl
import time
import threading
from typing import Optional
import paho.mqtt.client as mqtt

from backend.app.config import settings
from backend.app.mqtt.topics import TRAIN_CHECKPOINT_TOPIC_FILTER, COACH_DOOR_TOPIC_FILTER
from backend.app.mqtt.handlers import handle_mqtt_message
from backend.app.utils.logger import logger


class MQTTService:
    """Manages the backend MQTT connection to Mosquitto."""

    def __init__(self):
        # paho-mqtt v2 compatible callback API
        try:
            self.client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id="nammaflow_backend_server"
            )
        except AttributeError:
            self.client = mqtt.Client(client_id="nammaflow_backend_server")

        self.connected = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._setup_callbacks()

    def _setup_callbacks(self):
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = handle_mqtt_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        rc_code = rc if isinstance(rc, int) else getattr(rc, "value", 0)
        if rc_code == 0:
            self.connected = True
            logger.info(f"MQTT Connected successfully to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            # Subscribe to required telemetry topics
            self.client.subscribe([(TRAIN_CHECKPOINT_TOPIC_FILTER, 1), (COACH_DOOR_TOPIC_FILTER, 1)])
            logger.info(f"Subscribed to '{TRAIN_CHECKPOINT_TOPIC_FILTER}' and '{COACH_DOOR_TOPIC_FILTER}'")
        else:
            self.connected = False
            logger.error(f"MQTT connection refused with code {rc_code}")

    def _on_disconnect(self, client, userdata, disconnect_flags_or_rc, reason_code=None, properties=None):
        self.connected = False
        logger.warning("MQTT disconnected from broker. Reconnection loop active.")

    def start(self, non_blocking: bool = True):
        """Starts MQTT connection with optional TLS in background."""
        # Setup authentication
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        # Setup TLS if enabled
        if settings.MQTT_TLS_ENABLED and settings.MQTT_CA_CERT:
            try:
                self.client.tls_set(
                    ca_certs=settings.MQTT_CA_CERT,
                    certfile=settings.MQTT_CLIENT_CERT,
                    keyfile=settings.MQTT_CLIENT_KEY,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLS_CLIENT
                )
                logger.info("Configured MQTT TLS encryption.")
            except Exception as e:
                logger.error(f"Failed to configure MQTT TLS: {e}")

        if non_blocking:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
        else:
            self._run_loop()

    def _run_loop(self):
        """Continuous reconnection loop with non-blocking async connection."""
        backoff = 2.0
        while not self._stop_event.is_set():
            try:
                if not self.connected:
                    logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")
                    self.client.connect_async(
                        settings.MQTT_BROKER_HOST,
                        settings.MQTT_BROKER_PORT,
                        keepalive=settings.MQTT_KEEPALIVE
                    )
                    self.client.loop_start()
            except Exception as e:
                logger.warning(f"Could not initiate MQTT connection: {e}")
            
            # Wait for backoff interval or until stopped
            if self._stop_event.wait(timeout=backoff):
                break
            if not self.connected:
                backoff = min(15.0, backoff * 1.5)
            else:
                backoff = 2.0


    def stop(self):
        """Stops the MQTT client cleanly."""
        self._stop_event.set()
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
        self.connected = False
        logger.info("MQTT client stopped.")


mqtt_service = MQTTService()
