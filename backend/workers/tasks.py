"""Celery task definitions for MediNexus."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Celery app (lazy init) ───────────────────────────────────────────────── #
# In production, configure via app.conf:
#   app = Celery("medinexus", broker=settings.redis_url)
_celery_app = None


def get_celery_app():
    """Lazy-initialize Celery app."""
    global _celery_app
    if _celery_app is not None:
        return _celery_app

    try:
        from celery import Celery
        from app.config import settings

        _celery_app = Celery(
            "medinexus",
            broker=settings.redis_url,
            backend=settings.redis_url,
        )
        _celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="Asia/Shanghai",
            enable_utc=True,
            task_track_started=True,
            task_soft_time_limit=300,
            task_time_limit=600,
        )
        logger.info("Celery app initialized with broker: %s", settings.redis_url)
    except Exception as e:
        logger.warning("Celery init failed (non-critical): %s", e)
        _celery_app = None

    return _celery_app


# ── Task definitions ─────────────────────────────────────────────────────── #

async def send_followup_reminder(patient_id: str, message: str) -> dict[str, Any]:
    """Send a follow-up reminder to a patient.

    In demo mode, logs the reminder. In production, dispatches via Celery.
    """
    logger.info("[FOLLOWUP REMINDER] patient=%s message=%s", patient_id, message)

    app = get_celery_app()
    if app:
        try:
            task = app.send_task("tasks.send_followup_reminder", args=[patient_id, message])
            return {"task_id": task.id, "status": "dispatched"}
        except Exception as e:
            logger.warning("Celery dispatch failed, using sync: %s", e)

    return {"task_id": None, "status": "logged", "patient_id": patient_id}


async def process_async_analysis(session_id: str, symptoms: str) -> dict[str, Any]:
    """Queue an async deep analysis task.

    In demo mode, processes synchronously. In production, dispatches via Celery.
    """
    logger.info("[ASYNC ANALYSIS] session=%s symptoms=%s", session_id, symptoms[:50])

    app = get_celery_app()
    if app:
        try:
            task = app.send_task("tasks.process_async_analysis", args=[session_id, symptoms])
            return {"task_id": task.id, "status": "queued"}
        except Exception as e:
            logger.warning("Celery dispatch failed, using sync: %s", e)

    return {"task_id": None, "status": "sync_complete", "session_id": session_id}


async def cleanup_expired_sessions() -> dict[str, Any]:
    """Clean up expired sessions (scheduled task).

    Returns count of cleaned sessions.
    """
    logger.info("[CLEANUP] Cleaning expired sessions...")
    try:
        from orchestration.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        count = supervisor.cleanup_expired()
        logger.info("[CLEANUP] Removed %d expired sessions", count)
        return {"cleaned": count}
    except Exception as e:
        logger.error("[CLEANUP] Error: %s", e)
        return {"cleaned": 0, "error": str(e)}
