"""Context service providing weather, festival, and match-day context.

Scientific Rule: Rain and special events are treated as 'probable contributing factors',
never as sole causes of delays.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.app.database import db
from backend.app.utils.logger import logger


class ContextService:
    """Manages environmental and situational context for delay forecasting."""

    def __init__(self):
        self.calendar_path = settings.CALENDAR_PATH
        self._calendar_data = self._load_calendar()

    def _load_calendar(self) -> Dict[str, Any]:
        if self.calendar_path.exists():
            try:
                with open(self.calendar_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read calendar data: {e}")
        return {"festivals": [], "cricket_matches": [], "monsoon_months": [6, 7, 8, 9, 10]}

    def get_current_context(self, current_time: Optional[float] = None) -> Dict[str, Any]:
        """Evaluates rain, festival, and match flags for the current or given time.
        
        Supports demo overrides via the database context_state table.
        """
        now = current_time if current_time is not None else time.time()
        dt = datetime.fromtimestamp(now)
        date_str = dt.strftime("%Y-%m-%d")

        # Check database for demo manual overrides
        override_rain = db.get_context_override("rain")
        override_festival = db.get_context_override("festival")
        override_match = db.get_context_override("match_day")

        # Determine rain flag
        if override_rain is not None:
            rain = override_rain.lower() in ("true", "1", "yes")
        else:
            # By default during monsoon months, rain is considered possible/probable
            rain = dt.month in self._calendar_data.get("monsoon_months", [])

        # Determine festival flag
        if override_festival is not None:
            festival = override_festival.lower() in ("true", "1", "yes")
        else:
            festivals = [f["name"] for f in self._calendar_data.get("festivals", []) if f["date"] == date_str]
            festival = len(festivals) > 0

        # Determine match day flag
        if override_match is not None:
            match_day = override_match.lower() in ("true", "1", "yes")
        else:
            matches = [m["event"] for m in self._calendar_data.get("cricket_matches", []) if m["date"] == date_str]
            match_day = len(matches) > 0

        # Determine scientific probable factor tag
        # Rule: Never say 'cause'. Always say 'probable contributing factor'.
        if festival and rain:
            probable_factor = "festival and rain (probable contributing factors)"
        elif festival:
            probable_factor = "festival crowd (probable contributing factor)"
        elif match_day:
            probable_factor = "stadium match event (probable contributing factor)"
        elif rain:
            probable_factor = "rain (probable contributing factor)"
        else:
            probable_factor = "normal operations"

        is_override = any(o is not None for o in [override_rain, override_festival, override_match])

        return {
            "timestamp": now,
            "rain": rain,
            "festival": festival,
            "match_day": match_day,
            "probable_factor": probable_factor,
            "time_scale_factor": settings.TIME_SCALE_FACTOR,
            "is_demo_override_active": is_override,
            "override_details": {
                "rain_override": override_rain,
                "festival_override": override_festival,
                "match_override": override_match
            } if is_override else None
        }

    def set_demo_override(
        self,
        rain: Optional[bool] = None,
        festival: Optional[bool] = None,
        match_day: Optional[bool] = None,
        reset_to_real: bool = False
    ):
        """Allows dashboard/demo switcher to simulate rain or festival day."""
        if reset_to_real:
            with db.get_connection() as conn:
                conn.execute("DELETE FROM context_state WHERE key IN ('rain', 'festival', 'match_day')")
                conn.commit()
            logger.info("Demo context overrides reset to real calendar/weather state.")
            return

        if rain is not None:
            db.set_context_override("rain", "true" if rain else "false")
        if festival is not None:
            db.set_context_override("festival", "true" if festival else "false")
        if match_day is not None:
            db.set_context_override("match_day", "true" if match_day else "false")
        logger.info(f"Updated demo context: rain={rain}, festival={festival}, match_day={match_day}")


context_service = ContextService()
