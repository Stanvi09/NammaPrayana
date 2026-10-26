"""Time scale conversion utilities between hardware testbed and real metro time."""

from backend.app.config import settings


def track_seconds_to_metro_seconds(track_seconds: float, factor: float = None) -> float:
    """Converts testbed track seconds to scaled real-world metro seconds."""
    scale = factor if factor is not None else settings.TIME_SCALE_FACTOR
    return track_seconds * scale


def track_seconds_to_metro_minutes(track_seconds: float, factor: float = None) -> float:
    """Converts testbed track seconds to scaled real-world metro minutes."""
    return track_seconds_to_metro_seconds(track_seconds, factor) / 60.0


def metro_seconds_to_track_seconds(metro_seconds: float, factor: float = None) -> float:
    """Converts real-world metro seconds to testbed track seconds."""
    scale = factor if factor is not None else settings.TIME_SCALE_FACTOR
    if scale <= 0:
        raise ValueError("Time scale factor must be positive")
    return metro_seconds / scale


def metro_minutes_to_track_seconds(metro_minutes: float, factor: float = None) -> float:
    """Converts real-world metro minutes to testbed track seconds."""
    return metro_seconds_to_track_seconds(metro_minutes * 60.0, factor)
