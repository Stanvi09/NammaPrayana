"""API endpoints for security audit events and registered devices."""

from typing import List, Dict, Any
from fastapi import APIRouter, Query
from backend.app.database import db

router = APIRouter(prefix="/security", tags=["Security & Device Audit"])


@router.get("/events")
def get_security_audit_events(limit: int = 50):
    """Retrieves recent security alerts (e.g. forged signatures, replays, schema violations)."""
    lim = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 50
    events = db.get_recent_security_events(limit=lim)
    return {
        "count": len(events),
        "events": events
    }


@router.get("/devices")
def get_registered_devices():
    """Lists registered devices and their last-seen status (never leaks secrets or keys)."""
    devices = db.get_devices()
    return {
        "count": len(devices),
        "devices": devices
    }
