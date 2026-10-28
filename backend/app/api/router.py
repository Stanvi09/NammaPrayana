"""Aggregated API router for NammaFlow backend."""

from fastapi import APIRouter
from backend.app.api.train import router as train_router
from backend.app.api.delay import router as delay_router
from backend.app.api.crowd import router as crowd_router
from backend.app.api.context import router as context_router
from backend.app.api.security import router as security_router

api_router = APIRouter(prefix="/api")

api_router.include_router(train_router)
api_router.include_router(delay_router)
api_router.include_router(crowd_router)
api_router.include_router(context_router)
api_router.include_router(security_router)
