from datetime import datetime

import pandas as pd

import get_context as gc


def _cal(tmp_path):
    p = tmp_path / "cal.csv"
    pd.DataFrame([
        {"date": "2026-10-20", "name": "Dussehra", "type": "festival", "notes": ""},
        {"date": "2026-10-25", "name": "Test match", "type": "match", "notes": ""},
    ]).to_csv(p, index=False)
    return p


def _saved(tmp_path, mm):
    p = tmp_path / "rain.csv"
    pd.DataFrame({"datetime": ["2026-10-20 08:00"], "precip_mm": [mm]}).to_csv(p, index=False)
    return p


def test_festival_day(tmp_path):
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=False,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 0.0))
    assert c["festival_flag"] == 1 and c["event_name"] == "Dussehra"


def test_match_day_sets_festival_flag(tmp_path):
    c = gc.get_context(datetime(2026, 10, 25, 8), use_api=False,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 0.0))
    assert c["match_day"] and c["festival_flag"] == 1


def test_normal_day(tmp_path):
    c = gc.get_context(datetime(2026, 10, 22, 8), use_api=False,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 0.0))
    assert c["festival_flag"] == 0 and c["event_name"] == ""


def test_rain_from_saved_file(tmp_path):
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=False,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 2.4))
    assert c["rain_flag"] == 1 and c["rain_source"] == "saved_file"


def test_light_drizzle_is_not_rain(tmp_path):
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=False,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 0.2))
    assert c["rain_flag"] == 0


def test_api_failure_falls_back_to_saved(tmp_path, monkeypatch):
    def boom(dt):
        raise RuntimeError("no network")
    monkeypatch.setattr(gc, "_precip_from_api", boom)
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=True,
                       calendar_path=_cal(tmp_path), saved_path=_saved(tmp_path, 3.0))
    assert c["rain_source"] == "saved_file" and c["rain_flag"] == 1


def test_api_success(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "_precip_from_api", lambda dt: 1.0)
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=True,
                       calendar_path=_cal(tmp_path), saved_path=tmp_path / "none.csv")
    assert c["rain_source"] == "api" and c["rain_flag"] == 1


def test_everything_missing_is_safe(tmp_path):
    c = gc.get_context(datetime(2026, 10, 20, 8), use_api=False,
                       calendar_path=tmp_path / "x.csv", saved_path=tmp_path / "y.csv")
    assert c["rain_source"] == "none" and c["rain_flag"] == 0 and c["festival_flag"] == 0
