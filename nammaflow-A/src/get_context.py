"""Role A: get_context(datetime) -> rain yes/no and festival / match-day yes/no.

Rain   : Open-Meteo hourly precipitation for Bengaluru. If the API fails, falls back to
         data/rain_forecast_saved.csv (columns: datetime, precip_mm). If neither works,
         rain is reported as unknown (rain_flag = 0, rain_source = "none").
         If the saved file is used, SAY SO in the paper.
Festival: data/festival_calendar.csv (columns: date, name, type, notes).
         type is "festival" or "match". Add match days here (ask D to help fill it).

Save a forecast for offline use (needs internet):
    python src/get_context.py --save-forecast
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

LAT, LON = 12.9716, 77.5946          # Bengaluru
RAIN_MM = 0.5                        # >= this much in the hour counts as rain
API = "https://api.open-meteo.com/v1/forecast"
CALENDAR = Path("data/festival_calendar.csv")
SAVED = Path("data/rain_forecast_saved.csv")


def _precip_from_api(dt: datetime, timeout=5):
    import requests
    day = dt.strftime("%Y-%m-%d")
    r = requests.get(API, timeout=timeout, params=dict(
        latitude=LAT, longitude=LON, hourly="precipitation",
        timezone="Asia/Kolkata", start_date=day, end_date=day))
    r.raise_for_status()
    h = r.json()["hourly"]
    key = dt.strftime("%Y-%m-%dT%H:00")
    return float(h["precipitation"][h["time"].index(key)])


def _precip_from_saved(dt: datetime, path=SAVED):
    if not Path(path).exists():
        return None
    s = pd.read_csv(path)
    if s.empty:
        return None
    s["datetime"] = pd.to_datetime(s["datetime"])
    hit = s[s["datetime"] == pd.Timestamp(dt).floor("h")]
    return None if hit.empty else float(hit.precip_mm.iloc[0])


def _calendar_hits(dt: datetime, path=CALENDAR):
    if not Path(path).exists():
        return []
    cal = pd.read_csv(path, dtype=str).fillna("")
    return cal[cal["date"] == dt.strftime("%Y-%m-%d")].to_dict("records")


def get_context(dt: datetime, use_api=True, calendar_path=CALENDAR, saved_path=SAVED):
    """Returns a dict. The model only needs rain_flag and festival_flag."""
    precip, source = None, "none"
    if use_api:
        try:
            precip, source = _precip_from_api(dt), "api"
        except Exception:
            precip = None
    if precip is None:
        precip = _precip_from_saved(dt, saved_path)
        source = "saved_file" if precip is not None else "none"

    hits = _calendar_hits(dt, calendar_path)
    festival = any(h["type"] == "festival" for h in hits)
    match = any(h["type"] == "match" for h in hits)
    rain = bool(precip is not None and precip >= RAIN_MM)
    return {
        "rain": rain,
        "precip_mm": precip,
        "rain_source": source,          # "api", "saved_file" or "none"
        "festival": festival,
        "match_day": match,
        "event_name": ", ".join(h["name"] for h in hits),
        "rain_flag": int(rain),
        "festival_flag": int(festival or match),   # one flag for the model
    }


def save_forecast(days=7, path=SAVED):
    """Download the next few days of hourly precipitation to the saved file."""
    import requests
    r = requests.get(API, timeout=10, params=dict(
        latitude=LAT, longitude=LON, hourly="precipitation",
        timezone="Asia/Kolkata", forecast_days=days))
    r.raise_for_status()
    h = r.json()["hourly"]
    pd.DataFrame({"datetime": h["time"], "precip_mm": h["precipitation"]}).to_csv(path, index=False)
    print(f"saved {len(h['time'])} hourly rows to {path}")


if __name__ == "__main__":
    if "--save-forecast" in sys.argv:
        save_forecast()
    else:
        print(get_context(datetime.now()))
