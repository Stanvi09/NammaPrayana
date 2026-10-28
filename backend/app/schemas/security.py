from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SecurityEnvelope(BaseModel):
    """Cryptographic signature and anti-replay envelope for telemetry messages."""
    device_id: str = Field(..., min_length=1, max_length=64, description="Unique device ID")
    nonce: str = Field(..., min_length=8, max_length=128, description="Cryptographic nonce to prevent replay")
    timestamp: float = Field(..., ge=0, description="Message generation epoch timestamp")
    signature: str = Field(..., min_length=16, description="HMAC-SHA256 signature hex")
    payload: Dict[str, Any] = Field(..., description="Inner payload matching train or door schema")
