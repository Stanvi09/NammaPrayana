"""Run with: pytest test_decisions.py   (or: python test_decisions.py)"""
import pytest
from decisions import (leave_now, connection_saver, alternate_route,
                       false_alarm_rate)


# ---- Leave-Now
def test_leave_now_basic():
    r = leave_now(scheduled_departure=30, delay=6, travel_to_station=10, buffer=2)
    assert r.expected_train_time == 36
    assert r.leave_at == 24            # 36 - 10 - 2


def test_leave_now_no_delay():
    assert leave_now(30, 0, 10, 2).leave_at == 18


def test_leave_now_latest_safe_uses_range_top():
    r = leave_now(30, 6, 10, 2, delay_high=9)
    assert r.leave_at == 24 and r.latest_safe == 27


def test_leave_now_rejects_negative():
    with pytest.raises(ValueError):
        leave_now(30, -1, 10)


# ---- Connection-Saver
def test_connection_ok():
    a = connection_saver(scheduled_arrival=20, delay=1, delay_high=2,
                         transfer_time=4, connection_departure=30)
    assert a.status == "ok" and not a.alert and a.slack == 5


def test_connection_at_risk_alerts():
    a = connection_saver(20, delay=8, delay_high=10, transfer_time=4, connection_departure=30)
    assert a.status == "at_risk" and a.alert and a.slack == -2


def test_connection_watch_does_not_alert():
    # median fine, top of range would miss it -> watch only (limits false alarms)
    a = connection_saver(20, delay=4, delay_high=8, transfer_time=4, connection_departure=30)
    assert a.status == "watch" and not a.alert


def test_connection_exactly_on_time_is_ok():
    a = connection_saver(20, delay=6, delay_high=6, transfer_time=4, connection_departure=30)
    assert a.status == "ok" and a.slack == 0


def test_alert_lead_time():
    late = connection_saver(20, 8, 10, 4, 30, now=28)     # only 2 min before departure
    early = connection_saver(20, 8, 10, 4, 30, now=24)    # 6 min before
    assert not late.lead_ok and early.lead_ok


def test_bad_range_rejected():
    with pytest.raises(ValueError):
        connection_saver(20, delay=5, delay_high=3, transfer_time=4, connection_departure=30)


# ---- Alternate routes
def test_no_alternative_for_small_delay():
    assert alternate_route(delay=5, remaining_trip_if_wait=15) is None   # not over 5


def test_alternative_offered_when_faster():
    alt = alternate_route(delay=12, remaining_trip_if_wait=20)           # stay = 32 > 22
    assert alt is not None and alt["total_min"] == 22


def test_no_alternative_if_not_faster():
    assert alternate_route(delay=6, remaining_trip_if_wait=10) is None   # stay = 16 < 22


# ---- False-alarm rate
def test_false_alarm_rate():
    assert false_alarm_rate([True, True, True, False], [True, False, True, True]) == pytest.approx(1 / 3)
    assert false_alarm_rate([False, False], [True, True]) == 0.0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
