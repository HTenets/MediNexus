"""Episodic memory (tier 2) — records of past consultations.

Answers "what happened on this patient's previous visits?" so a returning
patient doesn't have to repeat themselves.

Primary store is the ``consultations`` table. Without a database, episodes are
kept in a module-level in-process store.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.core.database import AsyncSession, db_enabled

logger = logging.getLogger(__name__)

#: Process-local fallback for deployments without a database.
_FALLBACK: dict[str, list[dict]] = {}


class EpisodicMemory:
    """Past-visit recall for a patient, most recent first."""

    # ── Read ──────────────────────────────────────────────────────────── #

    async def recall(self, patient_id: str, limit: int = 5) -> list[dict]:
        """Return up to ``limit`` past consultations, newest first."""
        if not patient_id or limit <= 0:
            return []

        if db_enabled():
            episodes = await self._recall_from_db(patient_id, limit)
            if episodes is not None:
                return episodes

        return list(_FALLBACK.get(patient_id, []))[:limit]

    async def format_recall(self, patient_id: str, limit: int = 3) -> str:
        """Render past visits as a compact block for LLM context injection."""
        episodes = await self.recall(patient_id, limit=limit)
        if not episodes:
            return ""

        lines = []
        for ep in episodes:
            when = (ep.get("timestamp") or "")[:10]
            assessment = ep.get("assessment") or ep.get("diagnosis") or "未记录"
            lines.append(f"- {when or '日期未知'}: {assessment}")
        return "\n".join(lines)

    # ── Write ─────────────────────────────────────────────────────────── #

    async def store(
        self,
        patient_id: str,
        consultation_id: str,
        assessment: str = "",
        **extra: Any,
    ) -> bool:
        """Record a consultation episode. Returns True on success."""
        if not patient_id:
            return False

        episode = {
            "consultation_id": consultation_id,
            "assessment": assessment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **extra,
        }

        if db_enabled() and await self._store_in_db(patient_id, consultation_id, episode):
            return True

        _FALLBACK.setdefault(patient_id, []).insert(0, episode)
        return True

    # ── Database layer ────────────────────────────────────────────────── #

    async def _recall_from_db(self, patient_id: str, limit: int) -> list[dict] | None:
        from sqlalchemy import select
        from app.models import Consultation

        try:
            async with AsyncSession() as session:
                rows = (
                    await session.execute(
                        select(Consultation)
                        .where(Consultation.patient_id == patient_id)
                        .order_by(Consultation.updated_at.desc())
                        .limit(limit)
                    )
                ).scalars().all()
        except Exception as e:  # noqa: BLE001 - memory must never break the pipeline
            logger.warning("Episodic memory DB read failed for %s: %s", patient_id, e)
            return None

        episodes = []
        for row in rows:
            context = dict(row.context or {})
            episodes.append({
                "consultation_id": row.id,
                "assessment": row.diagnosis or context.get("assessment", ""),
                "diagnosis": context.get("diagnosis", ""),
                "timestamp": (row.updated_at or row.created_at).isoformat()
                if (row.updated_at or row.created_at)
                else "",
                "status": row.status,
            })
        return episodes

    async def _store_in_db(self, patient_id: str, consultation_id: str, episode: dict) -> bool:
        """Attach the episode to an existing consultation row.

        Episodic memory does not create consultations — the supervisor owns that
        lifecycle. If the session row doesn't exist yet, we report False so the
        caller keeps the episode in the fallback store.
        """
        from sqlalchemy import select
        from app.models import Consultation

        try:
            async with AsyncSession() as session:
                row = (
                    await session.execute(
                        select(Consultation).where(Consultation.id == consultation_id)
                    )
                ).scalar_one_or_none()
                if row is None:
                    return False

                context = dict(row.context or {})
                context["assessment"] = episode.get("assessment", "")
                context["episodic_stored_at"] = episode["timestamp"]
                # Re-assign: SQLAlchemy JSON columns don't track in-place mutation
                row.context = context
                row.diagnosis = episode.get("assessment") or row.diagnosis
                await session.commit()
                return True
        except Exception as e:  # noqa: BLE001
            logger.warning("Episodic memory DB write failed for %s: %s", patient_id, e)
            return False
