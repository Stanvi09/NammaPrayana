"""Message validator enforcing schema validation, authentication, integrity, and anti-replay."""

import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, Union
import jsonschema

from backend.app.config import settings, BASE_DIR
from backend.app.database import db
from backend.app.schemas.train import TrainMessage
from backend.app.schemas.door import DoorMessage
from backend.app.schemas.security import SecurityEnvelope
from backend.app.security.crypto import verify_signature, canonicalize
from backend.app.security.replay import replay_detector
from backend.app.utils.logger import logger


# Load JSON Schemas from schemas/ directory
TRAIN_SCHEMA_FILE = BASE_DIR / "schemas" / "train_message.json"
DOOR_SCHEMA_FILE = BASE_DIR / "schemas" / "door_message.json"

_train_json_schema = json.loads(TRAIN_SCHEMA_FILE.read_text(encoding="utf-8")) if TRAIN_SCHEMA_FILE.exists() else None
_door_json_schema = json.loads(DOOR_SCHEMA_FILE.read_text(encoding="utf-8")) if DOOR_SCHEMA_FILE.exists() else None


class MessageValidator:
    """Central validation gateway for all incoming MQTT and API telemetry."""

    def __init__(self, require_signatures: bool = None):
        self.require_signatures = (
            require_signatures if require_signatures is not None else settings.REQUIRE_SIGNATURES
        )

    def validate_raw_message(
        self,
        raw_message: Union[str, bytes, dict],
        expected_type: str,  # "train" or "door"
        source_ip_or_topic: Optional[str] = None,
        allow_historical_replay: bool = False
    ) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[str]]:
        """Parses, authenticates, verifies signatures, and validates schema.
        
        Returns:
            (is_valid, error_reason, parsed_payload, device_id)
        """
        # 1. Parse JSON
        if isinstance(raw_message, (str, bytes)):
            try:
                data = json.loads(raw_message)
            except Exception as e:
                reason = f"Malformed JSON: {str(e)}"
                logger.warning(reason)
                db.record_security_event(
                    event_type="MALFORMED_JSON",
                    device_id=None,
                    reason=reason,
                    payload_preview=str(raw_message),
                    source=source_ip_or_topic
                )
                return False, reason, None, None
        elif isinstance(raw_message, dict):
            data = raw_message
        else:
            reason = "Invalid message type (must be string, bytes, or dict)"
            return False, reason, None, None

        device_id = None
        payload = data

        # 2. Check for Security Envelope vs Raw Payload
        if "signature" in data and "device_id" in data:
            try:
                envelope = SecurityEnvelope(**data)
            except Exception as e:
                reason = f"Invalid security envelope structure: {str(e)}"
                logger.security(reason)
                db.record_security_event(
                    event_type="INVALID_ENVELOPE",
                    device_id=data.get("device_id"),
                    reason=reason,
                    payload_preview=str(data),
                    source=source_ip_or_topic
                )
                return False, reason, None, None

            device_id = envelope.device_id
            payload = envelope.payload

            # 2a. Authenticate device ID
            if device_id not in settings.DEVICE_KEYS:
                reason = f"Unknown or unauthorized device ID: '{device_id}'"
                logger.security(reason)
                db.record_security_event(
                    event_type="UNKNOWN_DEVICE",
                    device_id=device_id,
                    reason=reason,
                    payload_preview=str(payload),
                    source=source_ip_or_topic
                )
                return False, reason, None, device_id

            secret_key = settings.DEVICE_KEYS[device_id]

            # 2b. Check replay and timestamp freshness (unless explicit historical playback mode)
            if not allow_historical_replay:
                is_fresh, freshness_reason = replay_detector.check_and_record(
                    device_id=device_id,
                    nonce=envelope.nonce,
                    msg_timestamp=envelope.timestamp
                )
                if not is_fresh:
                    logger.security(f"Replay or stale check failed for {device_id}: {freshness_reason}")
                    db.record_security_event(
                        event_type="REPLAY_OR_STALE_ATTACK",
                        device_id=device_id,
                        reason=freshness_reason,
                        payload_preview=str(payload),
                        source=source_ip_or_topic
                    )
                    return False, freshness_reason, None, device_id

            # 2c. Verify cryptographic signature
            if not verify_signature(secret_key, payload, envelope.signature):
                reason = f"Signature verification failed for device '{device_id}'. Message forged or tampered."
                logger.security(reason)
                db.record_security_event(
                    event_type="SIGNATURE_VERIFICATION_FAILED",
                    device_id=device_id,
                    reason=reason,
                    payload_preview=str(payload),
                    source=source_ip_or_topic
                )
                return False, reason, None, device_id

            # Update device last_seen timestamp in database
            db.update_device_seen(device_id)

        else:
            # Message did not supply a security envelope
            if self.require_signatures:
                reason = "Rejected: Message lacks cryptographic signature envelope and REQUIRE_SIGNATURES is enabled."
                logger.security(reason)
                db.record_security_event(
                    event_type="UNSIGNED_MESSAGE_REJECTED",
                    device_id=None,
                    reason=reason,
                    payload_preview=str(data),
                    source=source_ip_or_topic
                )
                return False, reason, None, None

        # 3. Schema & Semantics Validation on inner payload
        if expected_type == "train":
            # JSON Schema check
            if _train_json_schema:
                try:
                    jsonschema.validate(instance=payload, schema=_train_json_schema)
                except jsonschema.ValidationError as e:
                    reason = f"JSON Schema validation failed for train message: {e.message}"
                    logger.warning(reason)
                    db.record_security_event("SCHEMA_VIOLATION", device_id, reason, str(payload), source_ip_or_topic)
                    return False, reason, None, device_id

            # Pydantic Model check
            try:
                validated_model = TrainMessage(**payload)
                return True, "Valid train message", validated_model.model_dump(), device_id
            except Exception as e:
                reason = f"Train message semantic validation error: {str(e)}"
                logger.warning(reason)
                db.record_security_event("INVALID_DATA", device_id, reason, str(payload), source_ip_or_topic)
                return False, reason, None, device_id

        elif expected_type == "door":
            # JSON Schema check
            if _door_json_schema:
                try:
                    jsonschema.validate(instance=payload, schema=_door_json_schema)
                except jsonschema.ValidationError as e:
                    reason = f"JSON Schema validation failed for door message: {e.message}"
                    logger.warning(reason)
                    db.record_security_event("SCHEMA_VIOLATION", device_id, reason, str(payload), source_ip_or_topic)
                    return False, reason, None, device_id

            # Pydantic Model check
            try:
                validated_model = DoorMessage(**payload)
                return True, "Valid door message", validated_model.model_dump(), device_id
            except Exception as e:
                reason = f"Door message semantic validation error: {str(e)}"
                logger.warning(reason)
                db.record_security_event("INVALID_DATA", device_id, reason, str(payload), source_ip_or_topic)
                return False, reason, None, device_id

        else:
            return False, f"Unknown expected type: {expected_type}", None, device_id


validator = MessageValidator()
