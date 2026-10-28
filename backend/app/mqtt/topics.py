"""MQTT topic definitions and matching utilities for NammaFlow."""

import re
from typing import Optional, Tuple

TRAIN_CHECKPOINT_TOPIC_FILTER = "nammaflow/train/+/checkpoint"
COACH_DOOR_TOPIC_FILTER = "nammaflow/coach/+/door"
SECURITY_ALERTS_TOPIC = "nammaflow/security/alerts"

_TRAIN_TOPIC_REGEX = re.compile(r"^nammaflow/train/([^/]+)/checkpoint$")
_DOOR_TOPIC_REGEX = re.compile(r"^nammaflow/coach/([^/]+)/door$")


def build_train_checkpoint_topic(train_id: str) -> str:
    return f"nammaflow/train/{train_id}/checkpoint"


def build_coach_door_topic(coach_id: str) -> str:
    return f"nammaflow/coach/{coach_id}/door"


def parse_train_topic(topic: str) -> Optional[str]:
    match = _TRAIN_TOPIC_REGEX.match(topic)
    return match.group(1) if match else None


def parse_door_topic(topic: str) -> Optional[str]:
    match = _DOOR_TOPIC_REGEX.match(topic)
    return match.group(1) if match else None
