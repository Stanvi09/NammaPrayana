"""One function for the backend: predict_for_api_sim(payload) -> JSON-ready dict.

    result = predict_for_api_sim({
        "timestamp": "2026-10-26T08:15:00",   # IST, ISO format (gives hour + weather + festival)
        "current_station": 3, "target_station": 8,      # 0-9, station indexes on B's line
        "current_delay": 4.0,                 # metro minutes late now
        "leader_delay": 2.0, "gap_to_leader": 6.0,      # train ahead (optional)
        "fault_now": 0, "recent_fault_min": 0,          # optional
        "crowd_max": 0.2, "crowd_mean": 0.15,           # optional, 0-1
        "commuter": {...}                     # optional, same as service.py
    })

rain_level and festival come from get_context(timestamp) unless you send them.
rain_level: 0 = under 0.5 mm/h, 1 = 0.5 to 2.5 mm/h, 2 = above 2.5 mm/h (ASSUMED mapping,
check with B how the simulator defines its levels).
"""
from dataclasses import asdict
from datetime import datetime

from decisions import alternate_route, connection_saver, leave_now
from get_context import get_context
from sim_predictor import predict_delay_sim

OPTIONAL = ("leader_delay", "gap_to_leader", "fault_now", "recent_fault_min", "crowd_max", "crowd_mean")


def _level(mm):
    if mm is None or mm < 0.5:
        return 0
    return 1 if mm < 2.5 else 2


def _r(d):
    return {k: round(v, 2) if isinstance(v, float) else v for k, v in d.items()}


def predict_for_api_sim(payload: dict) -> dict:
    ts = datetime.fromisoformat(payload["timestamp"])
    ctx = get_context(ts)
    row = {"current_station": payload["current_station"], "target_station": payload["target_station"],
           "current_delay": float(payload["current_delay"]), "hour": ts.hour,
           "rain_level": payload.get("rain_level", _level(ctx["precip_mm"])),
           "festival": payload.get("festival", ctx["festival_flag"])}
    for k in OPTIONAL:
        if payload.get(k) is not None:
            row[k] = float(payload[k])

    pred = predict_delay_sim(row)
    lo, hi = pred["range_min"]
    out = {"delay_min": pred["delay_min"], "range_min": [lo, hi],
           "probable_factor": pred["probable_factor"],
           "context": {k: ctx[k] for k in ("rain", "festival", "match_day", "event_name", "rain_source")}}

    c = payload.get("commuter")
    if c:
        out["leave_now"] = _r(asdict(leave_now(c["scheduled_departure"], pred["delay_min"],
                                               c["travel_to_station"], delay_high=hi)))
        if c.get("connection"):
            k = c["connection"]
            out["connection"] = _r(asdict(connection_saver(
                k["scheduled_arrival"], pred["delay_min"], hi, k["transfer_time"],
                k["connection_departure"], now=c.get("now"))))
        if c.get("remaining_trip_if_wait") is not None:
            out["alternate_route"] = alternate_route(pred["delay_min"], c["remaining_trip_if_wait"])
    return out
