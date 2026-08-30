"""Consultation session persistence (durable layer behind the supervisor)."""

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Consultation
from orchestration.state import SessionState


def _jsonable(value):
    """Normalize to JSON-native types (DB JSON columns lack a str fallback)."""
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))


def _status_for(agent: str) -> str:
    if agent == "complete":
        return "completed"
    if agent == "emergency_protocol":
        return "emergency"
    return "active"


async def save_session(session: AsyncSession, state: SessionState) -> None:
    row = await session.get(Consultation, state.session_id)
    if row is None:
        row = Consultation(
            id=state.session_id,
            patient_id=state.patient_id,
            owner_id=state.owner_id,
        )
        session.add(row)
    row.current_agent = state.current_agent
    row.status = _status_for(state.current_agent)
    # Assign fresh objects — SQLAlchemy JSON columns don't track in-place mutation
    row.history = _jsonable(list(state.history))
    row.context = _jsonable(dict(state.context))
    await session.commit()


async def load_session(session: AsyncSession, session_id: str) -> SessionState | None:
    row = await session.get(Consultation, session_id)
    if row is None:
        return None
    return SessionState(
        session_id=row.id,
        patient_id=row.patient_id,
        owner_id=row.owner_id,
        current_agent=row.current_agent or "triage",
        history=list(row.history or []),
        context=dict(row.context or {}),
    )
