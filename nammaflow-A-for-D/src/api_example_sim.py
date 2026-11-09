"""FastAPI route for the simulator-trained model. In the backend:

    from api_example_sim import router
    app.include_router(router)       # POST /predict
"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from sim_service import predict_for_api_sim

router = APIRouter()


class Connection(BaseModel):
    scheduled_arrival: float
    transfer_time: float
    connection_departure: float


class Commuter(BaseModel):
    now: Optional[float] = None
    scheduled_departure: float
    travel_to_station: float
    connection: Optional[Connection] = None
    remaining_trip_if_wait: Optional[float] = None


class PredictRequest(BaseModel):
    timestamp: str
    current_station: int
    target_station: int
    current_delay: float
    leader_delay: Optional[float] = None
    gap_to_leader: Optional[float] = None
    fault_now: Optional[float] = None
    recent_fault_min: Optional[float] = None
    crowd_max: Optional[float] = None
    crowd_mean: Optional[float] = None
    rain_level: Optional[int] = None
    festival: Optional[int] = None
    commuter: Optional[Commuter] = None


@router.post("/predict")
def predict(req: PredictRequest):
    return predict_for_api_sim(req.model_dump(exclude_none=True))
