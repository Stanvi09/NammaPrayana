"""Coach crowding tracker, best-coach recommendation, and fleet integration."""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.app.config import settings
from backend.app.database import db
from backend.app.crowd.model import crowd_model, STAIR_PROXIMITY_MAP
from backend.app.utils.logger import logger


class CrowdEngine:
    """Aggregates door counter telemetry across real and simulated coaches."""

    def __init__(self):
        # Current occupancy count per coach (C1 is real sensor, C2-C6 are simulated)
        self.occupancies: Dict[str, int] = {
            "C1": 18,
            "C2": 35,
            "C3": 42,
            "C4": 28,
            "C5": 16,
            "C6": 12,
        }
        self.real_sensor_coach = "C1"
        self.simulated_coaches = ["C2", "C3", "C4", "C5", "C6"]

    def process_door_event(
        self,
        coach_id: str,
        timestamp: float,
        people_in: int,
        people_out: int,
        is_simulated: bool = False
    ) -> Dict[str, Any]:
        """Updates occupancy, computes crowd classification, and determines the best coach."""
        current_occ = self.occupancies.get(coach_id, 20)
        new_occ = max(0, current_occ + people_in - people_out)
        self.occupancies[coach_id] = new_occ

        coach_idx = int(coach_id.replace("C", "")) if coach_id.startswith("C") else 1
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour + (dt.minute / 60.0)

        # ML prediction
        crowd_level = crowd_model.predict(new_occ, hour, coach_idx)

        # Re-evaluate best coach across the train
        best_coach_id = min(self.occupancies, key=self.occupancies.get)

        # Persist prediction to database
        db.insert_crowd_prediction(
            coach_id=coach_id,
            crowd_level=crowd_level,
            passenger_count=new_occ,
            is_simulated=is_simulated,
            best_coach_flag=(coach_id == best_coach_id)
        )

        logger.info(
            f"Crowd updated for Coach {coach_id}: In={people_in}, Out={people_out}, "
            f"Occupancy={new_occ}, Level={crowd_level} (simulated={is_simulated})"
        )

        return {
            "coach_id": coach_id,
            "passenger_count": new_occ,
            "crowd_level": crowd_level,
            "is_simulated": is_simulated,
            "is_best_coach": (coach_id == best_coach_id),
            "best_coach": best_coach_id,
            "timestamp": timestamp
        }

    def get_train_crowd_summary(self, train_id: str = "T1") -> Dict[str, Any]:
        """Returns the complete crowd snapshot across all 6 coaches."""
        now = time.time()
        dt = datetime.fromtimestamp(now)
        hour = dt.hour + (dt.minute / 60.0)

        best_coach_id = min(self.occupancies, key=self.occupancies.get)
        coaches_list = []

        for coach_idx in range(1, 7):
            cid = f"C{coach_idx}"
            occ = self.occupancies.get(cid, 20)
            level = crowd_model.predict(occ, hour, coach_idx)
            is_sim = (cid != self.real_sensor_coach)
            coaches_list.append({
                "coach_id": cid,
                "crowd_level": level,
                "passenger_count": occ,
                "is_simulated": is_sim,
                "is_best_coach": (cid == best_coach_id),
                "stair_proximity": STAIR_PROXIMITY_MAP.get(cid, "Normal")
            })

        return {
            "train_id": train_id,
            "best_coach": best_coach_id,
            "coaches": coaches_list,
            "real_sensor_coach": self.real_sensor_coach,
            "simulated_coaches": self.simulated_coaches,
            "timestamp": now
        }


crowd_engine = CrowdEngine()
