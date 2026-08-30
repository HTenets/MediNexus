"""Memory manager — hierarchical retrieval across the three memory tiers.

    tier 1  working   WorkingMemory   transient, per-session (Redis / process)
    tier 2  episodic  EpisodicMemory  past consultations  (PostgreSQL / process)
    tier 3  semantic  SemanticMemory  patient profile     (PostgreSQL / process)

``retrieve`` composes tiers 2 and 3 into a single block ready for LLM context
injection, and returns an empty string when nothing is known about the patient.
Every tier degrades gracefully, so a failure here can never break a consultation.
"""

import logging
from typing import Any

from memory.stores.episodic import EpisodicMemory
from memory.stores.semantic import SemanticMemory
from memory.working import WorkingMemory

logger = logging.getLogger(__name__)


class MemoryManager:
    """Orchestrates the three memory tiers behind one facade."""

    def __init__(
        self,
        working: WorkingMemory | None = None,
        episodic: EpisodicMemory | None = None,
        semantic: SemanticMemory | None = None,
    ):
        self.working = working or WorkingMemory()
        self.episodic = episodic or EpisodicMemory()
        self.semantic = semantic or SemanticMemory()

    # ── Retrieval ─────────────────────────────────────────────────────── #

    async def retrieve(self, patient_id: str, context: str | None = None) -> str:
        """Build the memory block for a patient.

        ``context`` is the current query (symptoms, free text). It is currently
        used only for logging/diagnostics — retrieval is keyed by patient — but
        is part of the signature so callers can pass it without branching.
        """
        if not patient_id:
            return ""

        sections: list[str] = []

        try:
            profile_text = await self.semantic.format_profile(patient_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("Semantic memory retrieval failed for %s: %s", patient_id, e)
            profile_text = ""
        if profile_text:
            sections.append("## 患者长期档案\n" + profile_text)

        try:
            recall_text = await self.episodic.format_recall(patient_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("Episodic memory retrieval failed for %s: %s", patient_id, e)
            recall_text = ""
        if recall_text:
            sections.append("## 既往就诊记录\n" + recall_text)

        return "\n\n".join(sections)

    # ── Storage ───────────────────────────────────────────────────────── #

    async def store(self, patient_id: str, memory_type: str, data: dict):
        """Route a fact to the tier that owns ``memory_type``."""
        if not patient_id:
            return None

        if memory_type in ("episode", "consultation"):
            return await self.episodic.store(
                patient_id,
                (data or {}).get("consultation_id", ""),
                assessment=(data or {}).get("assessment", ""),
                **(data or {}),
            )
        if memory_type in ("allergy", "condition", "medication", "note"):
            return await self.semantic.add_history(patient_id, memory_type, data)
        if memory_type == "working":
            session_id = (data or {}).get("session_id", "")
            return await self.working.set_context(session_id, (data or {}).get("context", {}))

        logger.warning("Unknown memory_type: %s", memory_type)
        return None

    async def store_consultation(
        self,
        patient_id: str,
        consultation_id: str,
        assessment: str = "",
        **extra: Any,
    ) -> bool:
        """Record a finished consultation as a new episode."""
        try:
            return await self.episodic.store(
                patient_id, consultation_id, assessment=assessment, **extra
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("store_consultation failed for %s: %s", patient_id, e)
            return False

    # ── Session (working tier) delegation ─────────────────────────────── #

    async def set_current_agent(self, session_id: str, agent: str) -> bool:
        return await self.working.set_current_agent(session_id, agent)

    async def get_current_agent(self, session_id: str) -> str | None:
        return await self.working.get_current_agent(session_id)

    async def set_context(self, session_id: str, context: dict) -> bool:
        return await self.working.set_context(session_id, context)

    async def get_context(self, session_id: str) -> dict:
        return await self.working.get_context(session_id)

    async def update_context(self, session_id: str, patch: dict) -> dict:
        return await self.working.update_context(session_id, patch)

    async def session_exists(self, session_id: str) -> bool:
        return await self.working.session_exists(session_id)

    async def delete_session(self, session_id: str) -> bool:
        return await self.working.delete_session(session_id)
