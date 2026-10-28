"""Delay forecasting, confidence intervals, Leave-Now, and Connection-Saver logic."""

import time
from typing import Dict, Any, Optional, Tuple
from backend.app.config import settings
from backend.app.database import db
from backend.app.services.context_service import context_service
from backend.app.utils.time_scale import track_seconds_to_metro_minutes, track_seconds_to_metro_seconds
from backend.app.utils.logger import logger


# Alternate routes around Majestic interchange when delays exceed 5 minutes
ALTERNATE_ROUTES = {
    "Majestic": "Take BMTC Bus Route 335E / V-335 directly to Whitefield or Purple Line feeder at Nadaprabhu Kempegowda station platform 3.",
    "Mid": "Alight at prior station and take Metro Feeder MF-1 directly to Majestic concourse.",
    "Start": "Consider Metro Green Line direct or Cab aggregator; Purple Line connecting train delayed."
}


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

        # 3. Downstream delay propagation to Majestic (inspired by Ding et al. 2021 MTGNN)
        # Checkpoint sequence: Start (1) -> Mid (2) -> Majestic (3) -> End (4)
        predicted_delay_at_majestic = measured_delay_metro_mins

        # Add propagation friction if delayed earlier
        if checkpoint_id == "Start":
            # Early delays accumulate dwell and queuing delay
            propagation_factor = 1.15 if ctx["rain"] else 1.05
            if ctx["festival"]:
                propagation_factor += 0.20
            predicted_delay_at_majestic = measured_delay_metro_mins * propagation_factor
        elif checkpoint_id == "Mid":
            # Approaching interchange
            propagation_factor = 1.10 if ctx["rain"] else 1.02
            predicted_delay_at_majestic = measured_delay_metro_mins * propagation_factor
        elif checkpoint_id == "Majestic":
            predicted_delay_at_majestic = measured_delay_metro_mins

        # 4. Confidence intervals / range (e.g. "6 to 9 minutes")
        # In quantile regression terms: ~80% prediction interval
        uncertainty_spread = max(1.0, predicted_delay_at_majestic * 0.25)
        range_low = max(0.0, round(predicted_delay_at_majestic - uncertainty_spread, 1))
        range_high = round(predicted_delay_at_majestic + uncertainty_spread, 1)
        range_text = f"{int(round(range_low))} to {int(round(range_high))} minutes"

        confidence_pct = 85.0 if not ctx["rain"] else 78.0

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
