"""Consultation API — REST endpoints for consultation management."""

import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.consultation import (
    ConsultationStartRequest,
    ConsultationStartResponse,
    ConsultationStatusResponse,
)
from orchestration.supervisor import supervisor
from orchestration.stream import StreamManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ConsultationStartResponse)
async def start_consultation(request: ConsultationStartRequest):
    """Start a new consultation session."""
    session_id = f"session_{uuid.uuid4().hex[:12]}"
    patient_id = request.patient_id or f"patient_{uuid.uuid4().hex[:8]}"
    session = await supervisor.create_session(session_id, patient_id)

    return ConsultationStartResponse(
        session_id=session.session_id,
        patient_id=session.patient_id,
        status="started",
        current_agent=session.current_agent,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/{consult_id}", response_model=ConsultationStatusResponse)
async def get_consultation(consult_id: str):
    """Get the current status of a consultation session."""
    session = await supervisor.get_session(consult_id)
    if not session:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="会话不存在")

    return ConsultationStatusResponse(
        session_id=session.session_id,
        patient_id=session.patient_id,
        status="active",
        current_agent=session.current_agent,
        history=session.history[-20:],
    )
