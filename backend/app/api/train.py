"""API endpoints for latest train checkpoint telemetry."""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.app.database import db
from backend.app.schemas.api_models import LatestTrainResponse
from backend.app.services.delay_engine import delay_engine
from backend.app.services.pipeline import pipeline
from backend.app.utils.time_scale import track_seconds_to_metro_minutes

router = APIRouter(prefix="/train", tags=["Train Telemetry"])


@router.get("/latest", response_model=LatestTrainResponse)
def get_latest_train_status(train_id: Optional[str] = None):
    """Retrieves the most recent verified train checkpoint telemetry."""
    # Ensure train_id is a clean string if provided
    tid = str(train_id) if (train_id and isinstance(train_id, str)) else None
    latest_event = db.get_latest_train_event(tid)

    if not latest_event:
        # Provide default testbed standby state if no events received yet
        return LatestTrainResponse(
            train_id=train_id or "T1",
            checkpoint_id="Start",
            timestamp=time.time(),
            scheduled_time=time.time(),
            delay_seconds=0.0,
            delay_metro_minutes=0.0,
            delay_range_minutes="0 to 1 minutes",
            probable_factor="normal operations",
            is_simulated=False,
            status="standby / waiting for first sensor pass"
        )

    t_delay_sec = latest_event["delay_seconds"]
    m_delay_min = track_seconds_to_metro_minutes(t_delay_sec)

    # Get latest prediction details
    latest_pred = db.get_latest_delay_prediction(latest_event["train_id"])
    range_text = (
        f"{int(round(latest_pred['range_low_minutes']))} to {int(round(latest_pred['range_high_minutes']))} minutes"
        if latest_pred else f"{int(m_delay_min)} to {int(m_delay_min + 2)} minutes"
    )
    factor = latest_pred["probable_factor"] if latest_pred else "normal operations"

    return LatestTrainResponse(
        train_id=latest_event["train_id"],
        checkpoint_id=latest_event["checkpoint_id"],
        timestamp=latest_event["timestamp"],
        scheduled_time=latest_event["scheduled_time"],
        delay_seconds=round(t_delay_sec, 2),
        delay_metro_minutes=round(m_delay_min, 2),
        delay_range_minutes=range_text,
        probable_factor=factor,
        is_simulated=bool(latest_event["is_simulated"]),
        status="in_transit"
    )


@router.post("/ingest")
def ingest_train_checkpoint(payload: dict):
    """Direct HTTP ingestion for train telemetry (useful for testing or fallback)."""
    success, reason, result = pipeline.ingest_train_message(
        raw_message=payload,
        source_origin="http_api",
        is_simulated=payload.get("is_simulated", False)
    )
    if not success:
        raise HTTPException(status_code=400, detail={"error": reason})
    return {"status": "accepted", "result": result}
