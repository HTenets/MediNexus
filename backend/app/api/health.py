"""Health check endpoint — returns system status."""

import logging

from fastapi import APIRouter
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check with demo mode awareness."""
    is_demo = settings.demo_mode or not settings.database_url
    return {
        "status": "ok",
        "mode": "demo" if is_demo else "production",
        "version": "0.1.0",
    }
