from typing import Literal
from pydantic import BaseModel, Field, field_validator


VALID_CHECKPOINTS = ("Start", "Mid", "Majestic", "End")


class TrainMessage(BaseModel):
    """Frozen track message format agreed in NammaFlow Project Plan."""
    train_id: str = Field(..., min_length=1, max_length=32, description="Train set ID (e.g., 'T1')")
    checkpoint_id: Literal["Start", "Mid", "Majestic", "End"] = Field(
        ..., description="Checkpoint location along the track"
    )
    timestamp: float = Field(..., ge=0, description="Unix epoch timestamp in seconds")
    scheduled_time: float = Field(..., ge=0, description="Scheduled timetable epoch in seconds")

    @field_validator("checkpoint_id")
    @classmethod
    def validate_checkpoint(cls, v: str) -> str:
        if v not in VALID_CHECKPOINTS:
            raise ValueError(f"Invalid checkpoint_id: {v}. Must be one of {VALID_CHECKPOINTS}")
        return v
