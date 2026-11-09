"""Delay forecasting, confidence intervals, Leave-Now, and Connection-Saver logic."""

import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd
from backend.app.database import db
from backend.app.services.context_service import context_service
from backend.app.utils.time_scale import track_seconds_to_metro_minutes
from backend.app.utils.logger import logger


# Alternate routes around Majestic interchange when delays exceed 5 minutes
ALTERNATE_ROUTES = {
    "Majestic": "Take BMTC Bus Route 335E / V-335 directly to Whitefield or Purple Line feeder at Nadaprabhu Kempegowda station platform 3.",
    "Mid": "Alight at prior station and take Metro Feeder MF-1 directly to Majestic concourse.",
    "Start": "Consider Metro Green Line direct or Cab aggregator; Purple Line connecting train delayed."
}

# The testbed checkpoints map onto Role A's 0..9 simulated line indexes.
MODEL_STATIONS = {"Start": 0, "Mid": 3, "Majestic": 8, "End": 9}
MODEL_PATH = Path(__file__).resolve().parents[3] / "nammaflow-A-for-D" / "models" / "sim_delay_model.joblib"


@lru_cache(maxsize=1)
def _load_simulator_model():
    return joblib.load(MODEL_PATH)


def _predict_at_majestic(checkpoint_id: str, delay: float, timestamp: float, ctx: Dict[str, Any]):
    """Run A-to-D's simulator-trained median and quantile estimators."""
    current_station = MODEL_STATIONS.get(checkpoint_id, MODEL_STATIONS["Start"])
    target_station = MODEL_STATIONS["Majestic"]
    if current_station >= target_station:
        return delay, delay, delay, "none"

    model = _load_simulator_model()
    dt = datetime.fromtimestamp(timestamp)
    row = {
        "current_station": current_station,
        "target_station": target_station,
        "current_delay": delay,
        "hour": dt.hour,
        # The backend context is boolean, so use the documented rain-present bucket.
        "rain_level": 1 if ctx["rain"] else 0,
        "festival": int(ctx["festival"] or ctx["match_day"]),
        "leader_delay": 0.0,
        "gap_to_leader": 6.0,
        "fault_now": 0.0,
        "recent_fault_min": 0.0,
        "crowd_max": 0.17,
        "crowd_mean": 0.15,
    }
    row.update({
        "stops_ahead": abs(target_station - current_station),
        "direction": 0 if target_station > current_station else 1,
        "target_is_interchange": int(target_station in (1, 8)),
    })
    x = pd.DataFrame([row])[model["features"]]
    base = float(delay)
    mid = max(0.0, base + float(model["median"].predict(x)[0]))
    low = min(mid, max(0.0, base + float(model["low"].predict(x)[0])))
    high = max(mid, base + float(model["high"].predict(x)[0]))

    factor, best_shift = "none", 0.5
    for column, label in (("rain_level", "rain"), ("festival", "festival")):
        if row[column]:
            without_factor = dict(row)
            without_factor[column] = 0
            off_x = pd.DataFrame([without_factor])[model["features"]]
            off_mid = max(0.0, base + float(model["median"].predict(off_x)[0]))
            shift = mid - off_mid
            if shift >= best_shift:
                factor, best_shift = label, shift
    return round(mid, 1), round(low, 1), round(high, 1), factor


class DelayEngine:
    """Predicts downstream arrival delays at Majestic interchange based on checkpoint telemetry."""

    def __init__(self):
        # Rolling history of recent checkpoint delays per train
        self.recent_delays: Dict[str, Dict[str, float]] = {}

    def process_checkpoint_event(
        self,
        train_id: str,
        checkpoint_id: str,
        timestamp: float,
        scheduled_time: float,
        is_simulated: bool = False
    ) -> Dict[str, Any]:
        """Calculates delay, predicts downstream arrival at Majestic, and evaluates commuter alerts."""
        # 1. Measured delay on testbed track (in track seconds)
        track_delay_seconds = timestamp - scheduled_time
        # Convert to scaled real metro minutes
        measured_delay_metro_mins = max(0.0, track_seconds_to_metro_minutes(track_delay_seconds))

        # Record in rolling history
        if train_id not in self.recent_delays:
            self.recent_delays[train_id] = {}
        self.recent_delays[train_id][checkpoint_id] = measured_delay_metro_mins

        # 2. Context evaluation (rain, festival, match day)
        ctx = context_service.get_current_context(timestamp)
        probable_factor = ctx["probable_factor"]

        # 3. Predict downstream delay at Majestic with A-to-D's trained model.
        predicted_delay_at_majestic, range_low, range_high, model_factor = _predict_at_majestic(
            checkpoint_id, measured_delay_metro_mins, timestamp, ctx
        )
        if model_factor != "none":
            probable_factor = f"{model_factor} (probable contributing factor)"
        range_text = f"{int(round(range_low))} to {int(round(range_high))} minutes"

        # The saved model's low/high estimators define an approximately 80% range.
        confidence_pct = 80.0

        # 5. Connection-Saver alert logic (Target: alert when delay > 5 mins threatening interchange connection)
        connection_saver_alert = predicted_delay_at_majestic >= 5.0
        alt_route = ALTERNATE_ROUTES.get(checkpoint_id, ALTERNATE_ROUTES["Majestic"]) if connection_saver_alert else None

        # 6. Leave-Now recommendation
        # If train is delayed, commuter departure window shifts
        commuter_walking_time_mins = 10.0
        adjusted_buffer = max(2.0, commuter_walking_time_mins - predicted_delay_at_majestic)
        leave_now_text = (
            f"Leave in {int(round(adjusted_buffer))} minutes to comfortably catch Train {train_id} at Majestic."
            if not connection_saver_alert
            else f"Connection at risk! {alt_route}"
        )

        # 7. Persist to database
        db.insert_delay_prediction(
            train_id=train_id,
            checkpoint_id=checkpoint_id,
            predicted_delay_minutes=round(predicted_delay_at_majestic, 2),
            range_low_minutes=range_low,
            range_high_minutes=range_high,
            confidence=confidence_pct,
            probable_factor=probable_factor,
            leave_now_recommendation=leave_now_text,
            connection_saver_alert=connection_saver_alert
        )

        logger.info(
            f"Prediction generated for Train {train_id} at {checkpoint_id}: "
            f"Delay={predicted_delay_at_majestic:.1f}m ({range_text}), Probable Factor='{probable_factor}'"
        )

        return {
            "train_id": train_id,
            "current_checkpoint": checkpoint_id,
            "measured_delay_metro_minutes": round(measured_delay_metro_mins, 2),
            "predicted_delay_minutes": round(predicted_delay_at_majestic, 2),
            "delay_range_low": range_low,
            "delay_range_high": range_high,
            "delay_range_text": range_text,
            "confidence_percentage": confidence_pct,
            "probable_factor": probable_factor,
            "leave_now_recommendation": leave_now_text,
            "connection_saver_alert": connection_saver_alert,
            "alternate_route_suggested": alt_route,
            "timestamp": timestamp,
            "is_simulated": is_simulated
        }


delay_engine = DelayEngine()
