"""API endpoints for weather, festival, match-day context, and demo switcher."""

from fastapi import APIRouter
from backend.app.schemas.api_models import ContextResponse, DemoSwitchRequest
from backend.app.services.context_service import context_service

router = APIRouter(prefix="/context", tags=["Context & Demo Switcher"])


@router.get("", response_model=ContextResponse)
def get_current_context():
    """Retrieves current weather, festival flags, and probable contributing factors."""
    return context_service.get_current_context()


@router.post("/demo-switch")
def update_demo_context_switch(req: DemoSwitchRequest):
    """Enables demo mode overrides (e.g. inject rain or festival day during live presentations)."""
    context_service.set_demo_override(
        rain=req.rain,
        festival=req.festival,
        match_day=req.match_day,
        reset_to_real=bool(req.reset_to_real)
    )
    return {
        "status": "updated",
        "current_context": context_service.get_current_context()
    }
