"""API endpoints for coach crowd predictions and best-coach advice."""

from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.api_models import CrowdResponse
from backend.app.services.crowd_engine import crowd_engine
from backend.app.services.pipeline import pipeline

router = APIRouter(prefix="/crowd", tags=["Coach Crowding"])


@router.get("", response_model=CrowdResponse)
def get_crowd_status(train_id: Optional[str] = "T1"):
    """Returns crowd density (Low, Medium, High) for each coach and best-coach recommendation.
    
    Clearly demarcates real hardware door sensors from simulated coaches.
    """
    tid = str(train_id) if (train_id and isinstance(train_id, str)) else "T1"
    summary = crowd_engine.get_train_crowd_summary(train_id=tid)
    return summary



@router.post("/ingest")
def ingest_door_count(payload: dict):
    """Direct HTTP ingestion for door sensor counter events."""
    success, reason, result = pipeline.ingest_door_message(
        raw_message=payload,
        source_origin="http_api",
        is_simulated=payload.get("is_simulated", False)
    )
    if not success:
        raise HTTPException(status_code=400, detail={"error": reason})
    return {"status": "accepted", "result": result}
