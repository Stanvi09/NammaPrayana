"""Security, cryptographic verification, anti-tampering, and replay protection tests."""

import time
import uuid
import pytest

from backend.app.config import settings
from backend.app.security.crypto import sign_message, verify_signature, canonicalize
from backend.app.security.replay import ReplayProtection
from backend.app.security.validator import MessageValidator


def test_canonicalize_order_invariance():
    """Verifies that dictionary key order does not alter canonical byte output."""
    d1 = {"b": 2, "a": 1, "nested": {"y": 20, "x": 10}}
    d2 = {"a": 1, "b": 2, "nested": {"x": 10, "y": 20}}
    assert canonicalize(d1) == canonicalize(d2)


def test_sign_and_verify_valid_signature():
    secret = "test_secret_key_123"
    data = {"train_id": "T1", "checkpoint_id": "Start", "timestamp": 100.0, "scheduled_time": 100.0}
    sig = sign_message(secret, data)
    assert verify_signature(secret, data, sig) is True


def test_tampered_payload_rejected():
    """Security objective: A modified message must fail signature verification."""
    secret = "train_secret_key_demo_01"
    original_data = {
        "train_id": "T1",
        "checkpoint_id": "Mid",
        "timestamp": 1729958400.0,
        "scheduled_time": 1729958400.0
    }
    signature = sign_message(secret, original_data)

    # Attacker alters delay: changes timestamp to make train appear severely late
    tampered_data = dict(original_data)
    tampered_data["timestamp"] = 1729958400.0 + 900.0  # +15 minutes fake delay

    assert verify_signature(secret, tampered_data, signature) is False


def test_validator_rejects_fake_train_delay():
    validator = MessageValidator(require_signatures=True)
    fake_msg = {
        "device_id": "esp32_train_01",
        "nonce": uuid.uuid4().hex,
        "timestamp": time.time(),
        "signature": "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff",  # Forged fake sig
        "payload": {
            "train_id": "T1",
            "checkpoint_id": "Mid",
            "timestamp": time.time(),
            "scheduled_time": time.time() - 600.0
        }
    }
    is_valid, reason, payload, dev_id = validator.validate_raw_message(fake_msg, expected_type="train")
    assert is_valid is False
    assert "Signature verification failed" in reason


def test_replay_attack_rejected():
    """A valid message must not be accepted repeatedly."""
    validator = MessageValidator(require_signatures=True)
    now = time.time()
    secret = settings.DEVICE_KEYS["esp32_train_01"]

    train_payload = {
        "train_id": "T1",
        "checkpoint_id": "Start",
        "timestamp": now,
        "scheduled_time": now
    }
    nonce = "unique_nonce_abc123"
    sig = sign_message(secret, train_payload)

    valid_msg = {
        "device_id": "esp32_train_01",
        "nonce": nonce,
        "timestamp": now,
        "signature": sig,
        "payload": train_payload
    }

    # First attempt: accepted
    ok1, reason1, _, _ = validator.validate_raw_message(valid_msg, expected_type="train")
    assert ok1 is True

    # Second attempt (replay attack): rejected!
    ok2, reason2, _, _ = validator.validate_raw_message(valid_msg, expected_type="train")
    assert ok2 is False
    assert "Replay detected" in reason2


def test_impossible_future_timestamp_rejected():
    replay_check = ReplayProtection(max_future_drift=60.0)
    now = 1000.0
    future_time = now + 500.0  # 500s into the future
    is_valid, reason = replay_check.check_and_record("dev1", "nonce1", future_time, current_time=now)
    assert is_valid is False
    assert "Impossible future timestamp" in reason


def test_stale_past_timestamp_rejected():
    replay_check = ReplayProtection(freshness_window=300.0)
    now = 1000.0
    stale_time = now - 600.0  # 10 minutes old
    is_valid, reason = replay_check.check_and_record("dev1", "nonce2", stale_time, current_time=now)
    assert is_valid is False
    assert "Stale message timestamp" in reason


def test_unknown_device_rejected():
    validator = MessageValidator(require_signatures=True)
    unauthorized_msg = {
        "device_id": "rogue_esp32_attacker",
        "nonce": uuid.uuid4().hex,
        "timestamp": time.time(),
        "signature": "deadbeefdeadbeefdeadbeefdeadbeef",
        "payload": {
            "train_id": "T1",
            "checkpoint_id": "Start",
            "timestamp": time.time(),
            "scheduled_time": time.time()
        }
    }
    is_valid, reason, _, _ = validator.validate_raw_message(unauthorized_msg, expected_type="train")
    assert is_valid is False
    assert "Unknown or unauthorized device ID" in reason
