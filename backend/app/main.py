"""NammaFlow FastAPI Backend Application.

Connects sensors, Mosquitto MQTT, SQLite database, delay forecaster,
crowd prediction ML model, and REST APIs for App/Dashboard.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import db
from backend.app.mqtt.client import mqtt_service
from backend.app.api.router import api_router
from backend.app.schemas.api_models import HealthResponse
from backend.app.services.watchdog import sensor_watchdog
from backend.app.utils.logger import logger

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NammaFlow Backend Server...")
    # Start MQTT connection in background if enabled
    if settings.MQTT_ENABLED:
        mqtt_service.start(non_blocking=True)
    yield
    # Shutdown
    logger.info("Shutting down NammaFlow Backend Server...")
    if settings.MQTT_ENABLED:
        mqtt_service.stop()



app = FastAPI(
    title="NammaFlow Backend & Telemetry API",
    description="Context-Aware, Data-Source-Agnostic Metro Delay & Coach-Crowd Testbed Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Role C's mobile app and web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """System health check endpoint verifying database, MQTT, and device connectivity."""
    uptime = time.time() - START_TIME
    db_ok = "connected"
    try:
        with db.get_connection() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        db_ok = f"error: {str(e)}"

    devices = db.get_devices()
    silent_alerts = sensor_watchdog.check_silent_sensors()

    overall_status = "healthy"
    if db_ok != "connected":
        overall_status = "unhealthy"
    elif not mqtt_service.connected or silent_alerts:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        uptime_seconds=round(uptime, 1),
        database=db_ok,
        mqtt_connected=mqtt_service.connected,
        registered_devices_count=len(devices),
        environment=settings.ENVIRONMENT,
        timestamp=time.time()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )
