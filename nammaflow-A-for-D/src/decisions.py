"""Role A: decision logic on top of predict_delay().

All times are metro minutes measured on one clock (e.g. minutes since 08:00).
predict_delay() gives the delay at Majestic as (mid, low, high).
Nothing here touches the model, so C and D can call these as plain functions.
"""
from dataclasses import dataclass

ALT_ROUTE_THRESHOLD = 5.0     # offer alternatives only when delay is over this (O4)
MIN_ALERT_LEAD = 3.0          # alert must come this early before departure (O3)

# Placeholder table of alternatives around Majestic. Replace the numbers with
# travel times from OpenRouteService once you have them.
# total_min = time from Majestic to the destination via that option.
ALTERNATIVES = [
    {"name": "Bus 500 series from Kempegowda bus stand", "total_min": 32},
    {"name": "Auto / cab to destination", "total_min": 22},
    {"name": "Walk to Magadi Road metro, then Green Line", "total_min": 28},
]


# ---------------------------------------------------------------- Leave-Now
@dataclass
class LeaveNow:
    leave_at: float          # recommended departure from home
    latest_safe: float       # latest time if the delay turns out to be at the top of the range
    expected_train_time: float


def leave_now(scheduled_departure, delay, travel_to_station, buffer=2.0, delay_high=None):
    """When should the commuter leave to catch the delayed train?

    scheduled_departure : timetable time the train leaves the commuter's station
    delay               : predicted delay (median) at that station, minutes
    travel_to_station   : walking / travel time from where they are
    buffer              : safety margin
    delay_high          : top of the predicted range (for latest_safe); defaults to delay
    """
    if delay < 0 or travel_to_station < 0 or buffer < 0:
        raise ValueError("delay, travel time and buffer must be >= 0")
    delay_high = delay if delay_high is None else max(delay, delay_high)
    train_time = scheduled_departure + delay
    return LeaveNow(
        leave_at=train_time - travel_to_station - buffer,
        latest_safe=scheduled_departure + delay_high - travel_to_station - buffer,
        expected_train_time=train_time,
    )


# --------------------------------------------------------- Connection-Saver
@dataclass
class ConnectionAlert:
    status: str               # "ok", "watch" or "at_risk"
    slack: float              # minutes to spare using the median delay (negative = missed)
    slack_worst: float        # minutes to spare using the top of the range
    alert: bool               # True only for "at_risk"
    lead_ok: bool             # alert comes at least MIN_ALERT_LEAD before departure


def connection_saver(scheduled_arrival, delay, delay_high, transfer_time,
                     connection_departure, now=None):
    """Will the commuter miss their connection at Majestic?

    status "at_risk": median prediction already misses it -> alert.
    status "watch"  : only the top of the range misses it -> no alert,
                      so we do not cry wolf (this keeps false alarms low, O7).
    now             : current metro time, used to check the 3-minute lead (O3).
    """
    if delay_high < delay:
        raise ValueError("delay_high must be >= delay")
    latest_ok = connection_departure - transfer_time
    slack = latest_ok - (scheduled_arrival + delay)
    slack_worst = latest_ok - (scheduled_arrival + delay_high)

    if slack < 0:
        status = "at_risk"
    elif slack_worst < 0:
        status = "watch"
    else:
        status = "ok"

    lead_ok = True if now is None else (connection_departure - now) >= MIN_ALERT_LEAD
    return ConnectionAlert(status, slack, slack_worst, status == "at_risk", lead_ok)


# --------------------------------------------------------- Alternate routes
def alternate_route(delay, remaining_trip_if_wait, alternatives=ALTERNATIVES):
    """Suggest an alternative only when the delay is over 5 minutes and it is quicker.

    remaining_trip_if_wait : minutes from Majestic to destination if they stay on the metro
    Returns the best alternative dict, or None.
    """
    if delay <= ALT_ROUTE_THRESHOLD:
        return None
    stay_total = delay + remaining_trip_if_wait
    best = min(alternatives, key=lambda a: a["total_min"])
    return best if best["total_min"] < stay_total else None


# -------------------------------------------------------------- Evaluation
def false_alarm_rate(alerted, actually_missed):
    """O7: of all alerts raised, the share where the connection was NOT missed.
    alerted, actually_missed: equal-length lists of bool."""
    alerts = [m for a, m in zip(alerted, actually_missed) if a]
    return 0.0 if not alerts else sum(1 for m in alerts if not m) / len(alerts)
