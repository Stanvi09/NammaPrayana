"""MQTT message arrival callbacks and routing into IngestionPipeline."""

import json
from typing import Any
import paho.mqtt.client as mqtt

from backend.app.mqtt.topics import parse_train_topic, parse_door_topic, SECURITY_ALERTS_TOPIC
from backend.app.services.pipeline import pipeline
from backend.app.utils.logger import logger


def handle_mqtt_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
    """Routes incoming MQTT topic messages to appropriate handlers."""
    topic = message.topic
    payload_str = message.payload.decode("utf-8", errors="replace")

    train_id = parse_train_topic(topic)
    if train_id:
        logger.info(f"MQTT incoming on {topic}: payload size={len(payload_str)} bytes")
        success, reason, result = pipeline.ingest_train_message(
            raw_message=payload_str,
            source_origin=f"mqtt:{topic}"
        )
        if not success:
            logger.security(f"Rejected train message on {topic}: {reason}")
            # Optionally publish alert to security topic
            alert_payload = json.dumps({"topic": topic, "reason": reason})
            client.publish(SECURITY_ALERTS_TOPIC, alert_payload)
        return

    coach_id = parse_door_topic(topic)
    if coach_id:
        logger.info(f"MQTT incoming on {topic}: payload size={len(payload_str)} bytes")
        success, reason, result = pipeline.ingest_door_message(
            raw_message=payload_str,
            source_origin=f"mqtt:{topic}"
        )
        if not success:
            logger.security(f"Rejected door message on {topic}: {reason}")
            alert_payload = json.dumps({"topic": topic, "reason": reason})
            client.publish(SECURITY_ALERTS_TOPIC, alert_payload)
        return

    logger.warning(f"MQTT received message on unhandled topic: {topic}")
