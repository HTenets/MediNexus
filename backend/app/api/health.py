"""Health check endpoint — returns system status."""

import logging

from fastapi import APIRouter
from app.config import settings
from app.core.database import db_enabled

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check with demo mode awareness."""
    payload = {
        "status": "ok",
        "mode": "demo" if settings.demo_mode else "production",
        "database": "connected" if db_enabled() else "none",
        "version": "0.1.1",
    }
    if settings.demo_mode and db_enabled():
        payload["demo_credentials"] = {
            "patient": {"email": "demo@medinexus.dev", "password": "Demo@12345"},
            "doctor": {"email": "doctor@medinexus.dev", "password": "Demo@12345"},
        }
    return payload
