"""API endpoints for predicted delay, ranges, and commuter guidance."""

import time
from typing import Optional
from fastapi import APIRouter, Query

from backend.app.database import db
from backend.app.schemas.api_models import DelayResponse
from backend.app.services.context_service import context_service
from backend.app.services.delay_engine import ALTERNATE_ROUTES

router = APIRouter(prefix="/delay", tags=["Delay Prediction & Guidance"])


@router.get("", response_model=DelayResponse)
def get_delay_prediction(train_id: Optional[str] = None):
    """Retrieves predicted delay at Majestic interchange, confidence range, and Leave-Now advice."""
    tid_query = str(train_id) if (train_id and isinstance(train_id, str)) else None
    latest_pred = db.get_latest_delay_prediction(tid_query)
    latest_event = db.get_latest_train_event(tid_query)

    curr_cp = latest_event["checkpoint_id"] if latest_event else "Start"
    tid = train_id or (latest_event["train_id"] if latest_event else "T1")

    if latest_pred:
        range_low = latest_pred["range_low_minutes"]
        range_high = latest_pred["range_high_minutes"]
        range_text = f"{int(round(range_low))} to {int(round(range_high))} minutes"
        pred_delay = latest_pred["predicted_delay_minutes"]
        conf = latest_pred["confidence"]
        factor = latest_pred["probable_factor"]
        leave_now = latest_pred["leave_now_recommendation"]
        alert = bool(latest_pred["connection_saver_alert"])
        alt_route = ALTERNATE_ROUTES.get(curr_cp, ALTERNATE_ROUTES["Majestic"]) if alert else None
        ts = latest_pred["created_at"]
    else:
        # Default nominal state
        ctx = context_service.get_current_context()
        pred_delay = 0.0
        range_low, range_high = 0.0, 1.0
        range_text = "0 to 1 minutes"
        conf = 90.0
        factor = ctx["probable_factor"]
        leave_now = "Leave as scheduled for Majestic interchange."
        alert = False
        alt_route = None
        ts = time.time()

    return DelayResponse(
        train_id=tid,
        current_checkpoint=curr_cp,
        predicted_delay_minutes=round(pred_delay, 1),
        delay_range_low=range_low,
        delay_range_high=range_high,
        delay_range_text=range_text,
        confidence_percentage=conf,
        probable_factor=factor,
        leave_now_recommendation=leave_now,
        connection_saver_alert=alert,
        alternate_route_suggested=alt_route,
        timestamp=ts
    )
