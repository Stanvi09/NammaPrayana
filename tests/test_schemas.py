"""Tests for frozen message formats and JSON schema enforcement."""

import json
from pathlib import Path
import pytest
import jsonschema

from backend.app.config import BASE_DIR
from backend.app.schemas.train import TrainMessage
from backend.app.schemas.door import DoorMessage

TRAIN_SCHEMA_FILE = BASE_DIR / "schemas" / "train_message.json"
DOOR_SCHEMA_FILE = BASE_DIR / "schemas" / "door_message.json"

train_schema = json.loads(TRAIN_SCHEMA_FILE.read_text(encoding="utf-8"))
door_schema = json.loads(DOOR_SCHEMA_FILE.read_text(encoding="utf-8"))


def test_valid_train_message_schema():
    valid_train = {
        "train_id": "T1",
        "checkpoint_id": "Start",
        "timestamp": 1729958400.0,
        "scheduled_time": 1729958400.0
    }
    # Validate against JSON schema
    jsonschema.validate(instance=valid_train, schema=train_schema)
    # Validate against Pydantic
    model = TrainMessage(**valid_train)
    assert model.train_id == "T1"
    assert model.checkpoint_id == "Start"


def test_invalid_train_checkpoint_rejected():
    invalid_train = {
        "train_id": "T1",
        "checkpoint_id": "UnknownStation",
        "timestamp": 1729958400.0,
        "scheduled_time": 1729958400.0
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_train, schema=train_schema)

    with pytest.raises(ValueError):
        TrainMessage(**invalid_train)


def test_missing_train_fields_rejected():
    missing_fields = {
        "train_id": "T1",
        "checkpoint_id": "Mid"
        # Missing timestamp and scheduled_time
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=missing_fields, schema=train_schema)


def test_valid_door_message_schema():
    valid_door = {
        "coach_id": "C1",
        "timestamp": 1729958400.0,
        "people_in": 12,
        "people_out": 4
    }
    jsonschema.validate(instance=valid_door, schema=door_schema)
    model = DoorMessage(**valid_door)
    assert model.coach_id == "C1"
    assert model.people_in == 12
    assert model.people_out == 4


def test_negative_people_count_rejected():
    negative_in = {
        "coach_id": "C1",
        "timestamp": 1729958400.0,
        "people_in": -5,
        "people_out": 2
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=negative_in, schema=door_schema)

    with pytest.raises(ValueError):
        DoorMessage(**negative_in)


def test_invalid_coach_id_rejected():
    invalid_coach = {
        "coach_id": "C99",
        "timestamp": 1729958400.0,
        "people_in": 5,
        "people_out": 0
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_coach, schema=door_schema)

    with pytest.raises(ValueError):
        DoorMessage(**invalid_coach)
