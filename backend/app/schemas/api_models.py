from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    uptime_seconds: float
    database: str
    mqtt_connected: bool
    registered_devices_count: int
    environment: str
    timestamp: float


class LatestTrainResponse(BaseModel):
    train_id: str
    checkpoint_id: str
    timestamp: float
    scheduled_time: float
    delay_seconds: float
    delay_metro_minutes: float
    delay_range_minutes: str
    probable_factor: str
    is_simulated: bool
    status: str


class DelayResponse(BaseModel):
    train_id: str
    current_checkpoint: str
    predicted_delay_minutes: float
    delay_range_low: float
    delay_range_high: float
    delay_range_text: str  # e.g. "6 to 9 minutes"
    confidence_percentage: float
    probable_factor: str  # "rain", "festival", "match_day", "none" (probable contributing factor)
    leave_now_recommendation: Optional[str]
    connection_saver_alert: bool
    alternate_route_suggested: Optional[str]
    timestamp: float


class CoachCrowdInfo(BaseModel):
    coach_id: str
    crowd_level: Literal["Low", "Medium", "High"]
    passenger_count: int
    is_simulated: bool
    is_best_coach: bool
    stair_proximity: str  # e.g. "Adjacent to Stairs", "Far from Stairs"


class CrowdResponse(BaseModel):
    train_id: str
    best_coach: str
    coaches: List[CoachCrowdInfo]
    real_sensor_coach: str
    simulated_coaches: List[str]
    timestamp: float


class ContextResponse(BaseModel):
    timestamp: float
    rain: bool
    festival: bool
    match_day: bool
    probable_factor: str
    time_scale_factor: float
    is_demo_override_active: bool
    override_details: Optional[dict] = None


class DemoSwitchRequest(BaseModel):
    rain: Optional[bool] = None
    festival: Optional[bool] = None
    match_day: Optional[bool] = None
    reset_to_real: Optional[bool] = False
