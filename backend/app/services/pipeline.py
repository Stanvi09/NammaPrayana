"""Unified Ingestion Pipeline for NammaFlow.

Both LIVE hardware (MQTT) and RECORDED source-swap feeds pass through
this identical pipeline:
Validator -> Cryptographic Auth -> Database -> Delay/Crowd Model -> API State.
"""

import json
import time
from typing import Dict, Any, Tuple, Optional, Union

from backend.app.database import db
from backend.app.security.validator import validator
from backend.app.services.delay_engine import delay_engine
from backend.app.services.crowd_engine import crowd_engine
from backend.app.services.watchdog import sensor_watchdog
from backend.app.utils.logger import logger


class IngestionPipeline:
    """Core end-to-end ingestion pipeline."""

    def ingest_train_message(
        self,
        raw_message: Union[str, bytes, dict],
        source_origin: str = "mqtt",
        is_simulated: bool = False,
        allow_historical_replay: bool = False
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Ingests, validates, persists, and predicts for a train checkpoint message."""
        start_time = time.perf_counter()

        # 1. Validation & Cryptographic Auth
        is_valid, reason, payload, device_id = validator.validate_raw_message(
            raw_message=raw_message,
            expected_type="train",
            source_ip_or_topic=source_origin,
            allow_historical_replay=allow_historical_replay
        )

        if not is_valid or payload is None:
            return False, reason, None

        # 2. Watchdog activity update
        if device_id:
            sensor_watchdog.record_activity(device_id, payload["timestamp"])

        # 3. Store raw message in database
        raw_str = json.dumps(raw_message) if not isinstance(raw_message, str) else raw_message
        delay_sec = payload["timestamp"] - payload["scheduled_time"]
        
        db.insert_train_event(
            train_id=payload["train_id"],
            checkpoint_id=payload["checkpoint_id"],
            timestamp=payload["timestamp"],
            scheduled_time=payload["scheduled_time"],
            delay_seconds=delay_sec,
            is_simulated=is_simulated,
            raw_payload=raw_str
        )

        # 4. Predict delay and evaluate alerts
        prediction_result = delay_engine.process_checkpoint_event(
            train_id=payload["train_id"],
            checkpoint_id=payload["checkpoint_id"],
            timestamp=payload["timestamp"],
            scheduled_time=payload["scheduled_time"],
            is_simulated=is_simulated
        )

        processing_latency_ms = (time.perf_counter() - start_time) * 1000.0
        prediction_result["processing_latency_ms"] = round(processing_latency_ms, 2)
        prediction_result["source_origin"] = source_origin

        return True, "Train message processed successfully", prediction_result

    def ingest_door_message(
        self,
        raw_message: Union[str, bytes, dict],
        source_origin: str = "mqtt",
        is_simulated: bool = False,
        allow_historical_replay: bool = False
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Ingests, validates, persists, and classifies coach crowd density."""
        start_time = time.perf_counter()

        # 1. Validation & Cryptographic Auth
        is_valid, reason, payload, device_id = validator.validate_raw_message(
            raw_message=raw_message,
            expected_type="door",
            source_ip_or_topic=source_origin,
            allow_historical_replay=allow_historical_replay
        )

        if not is_valid or payload is None:
            return False, reason, None

        # 2. Watchdog activity update
        if device_id:
            sensor_watchdog.record_activity(device_id, payload["timestamp"])

        # 3. Store raw message in database
        raw_str = json.dumps(raw_message) if not isinstance(raw_message, str) else raw_message
        
        db.insert_door_event(
            coach_id=payload["coach_id"],
            timestamp=payload["timestamp"],
            people_in=payload["people_in"],
            people_out=payload["people_out"],
            is_simulated=is_simulated,
            raw_payload=raw_str
        )

        # 4. Process crowding in CrowdEngine
        crowd_result = crowd_engine.process_door_event(
            coach_id=payload["coach_id"],
            timestamp=payload["timestamp"],
            people_in=payload["people_in"],
            people_out=payload["people_out"],
            is_simulated=is_simulated
        )

        processing_latency_ms = (time.perf_counter() - start_time) * 1000.0
        crowd_result["processing_latency_ms"] = round(processing_latency_ms, 2)
        crowd_result["source_origin"] = source_origin

        return True, "Door message processed successfully", crowd_result


pipeline = IngestionPipeline()
