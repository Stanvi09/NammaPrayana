"""Prediction with the model trained on B's simulator laps (models/sim_delay_model.joblib).

    from sim_predictor import predict_delay_sim
    predict_delay_sim({"current_station": 3, "target_station": 8, "current_delay": 4.0,
                       "leader_delay": 2.0, "gap_to_leader": 6.0, "hour": 8,
                       "rain_level": 1, "festival": 0})
    -> {"delay_min": 4.6, "range_min": (3.9, 6.1), "probable_factor": "rain"}

Needs the SAME scikit-learn version the model was trained with (see requirements.txt).
Interchange stations in B's simulator are 1 and 8. Missing optional inputs default to 0.
"""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "sim_delay_model.joblib"
INTERCHANGES = (1, 8)
MIN_SHIFT = 0.5            # metro minutes a flag must add before we name it
DEFAULTS = {"leader_delay": 0.0, "gap_to_leader": 6.0, "fault_now": 0.0,
            "recent_fault_min": 0.0, "crowd_max": 0.17, "crowd_mean": 0.15,
            "rain_level": 0, "festival": 0}


@lru_cache(maxsize=2)
def load_model(path: str = str(MODEL_PATH)):
    return joblib.load(path)          # loaded once, then reused


def _row(d: dict) -> dict:
    r = {**DEFAULTS, **d}
    cur, tgt = int(r["current_station"]), int(r["target_station"])
    if cur == tgt:
        raise ValueError("current_station and target_station must differ")
    r["stops_ahead"] = abs(tgt - cur)
    r["direction"] = 0 if tgt > cur else 1
    r["target_is_interchange"] = int(tgt in INTERCHANGES)
    return r


def predict_delay_sim(d: dict, model_path: str = str(MODEL_PATH)):
    m = load_model(str(model_path))
    r = _row(d)
    x = pd.DataFrame([r])[m["features"]]
    base = float(r["current_delay"])
    mid = max(0.0, base + float(m["median"].predict(x)[0]))
    lo = min(mid, max(0.0, base + float(m["low"].predict(x)[0])))
    hi = max(mid, base + float(m["high"].predict(x)[0]))

    factor, best = "none", MIN_SHIFT
    for col, label in [("rain_level", "rain"), ("festival", "festival")]:
        if r[col]:
            off = pd.DataFrame([{**r, col: 0}])[m["features"]]
            shift = mid - max(0.0, base + float(m["median"].predict(off)[0]))
            if shift >= best:
                factor, best = label, shift
    return {"delay_min": round(mid, 1), "range_min": (round(lo, 1), round(hi, 1)),
            "probable_factor": factor}
