import re
from pydantic import BaseModel, Field, field_validator


COACH_REGEX = re.compile(r"^C[1-6]$")


class DoorMessage(BaseModel):
    """Frozen coach door message format agreed in NammaFlow Project Plan."""
    coach_id: str = Field(..., description="Coach identifier (C1 through C6)")
    timestamp: float = Field(..., ge=0, description="Unix epoch timestamp in seconds")
    people_in: int = Field(..., ge=0, description="Non-negative count of passengers entering")
    people_out: int = Field(..., ge=0, description="Non-negative count of passengers exiting")

    @field_validator("coach_id")
    @classmethod
    def validate_coach_id(cls, v: str) -> str:
        if not COACH_REGEX.match(v):
            raise ValueError(f"Invalid coach_id: '{v}'. Must match pattern C1 through C6.")
        return v
