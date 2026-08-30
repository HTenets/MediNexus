"""SupervisorAgent — manages session state and routes patients to the correct agent.

Sessions are stored in-memory by default. When REDIS_URL is configured,
sessions are serialized to Redis so they persist across restarts and are
shared across multiple Uvicorn workers. When a database is configured,
sessions are additionally persisted to PostgreSQL as the durable layer.
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from agents.registry import registry
from app.config import settings
from app.core.database import AsyncSession, db_enabled
from app.repositories import consultation_repo
from app.schemas.agent import HandoverManifest
from memory.manager import MemoryManager
from orchestration.state import SessionState

logger = logging.getLogger(__name__)

# Optional Redis client for distributed session storage
_redis = None
if settings.redis_url:
    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        logger.info("Session store: Redis connected at %s", settings.redis_url)
    except ImportError:
        logger.warning("redis package not installed — sessions will use in-memory store")
    except Exception as e:
        logger.warning("Redis connection failed (%s) — falling back to in-memory store", e)

_SESSION_KEY_PREFIX = "medinexus:session:"
_SESSION_TTL = 3600  # 1 hour


class SupervisorAgent:
    """Routes patients to the appropriate agent and manages the consultation flow.

    Responsibilities:
      - Determine the next agent based on triage result & conversation context
      - Maintain session state and history (Redis-backed when available)
      - Coordinate multi-step flows (triage → doctor → review → followup)
    """

    def __init__(self, memory: MemoryManager | None = None, rag_query=None):
        self._sessions: dict[str, SessionState] = {}
        self.memory = memory or MemoryManager()
        # Shared retrieval stack injected into agents that support it
        # (ReviewAgent). Stays None when RAG is unavailable.
        self.rag_query = rag_query

    async def route(self, session: SessionState, context: dict[str, Any]) -> str:
        """Determine which agent should handle the next step."""
        current = session.current_agent

        if current == "triage":
            triage_result = context.get("triage_result", {})
            department = triage_result.get("department", "")
            urgency = triage_result.get("urgency", "routine")

            if urgency == "emergency":
                return "emergency_protocol"

            if department and department != "general":
                context["target_department"] = department

            return "doctor"

        elif current == "doctor":
            if context.get("needs_review", True):
                return "review"
            return "followup"

        elif current == "review":
            review_approved = context.get("review_approved", True)
            if not review_approved:
                logger.info("Review flagged issues, returning to doctor for revision")
                return "doctor"
            return "followup"

        elif current == "followup":
            return "complete"

        elif current == "coordinator":
            return "review"

        return "complete"

    async def create_session(self, session_id: str, patient_id: str, owner_id: str | None = None) -> SessionState:
        """Create a new consultation session."""
        session = SessionState(
            session_id=session_id,
            patient_id=patient_id,
            owner_id=owner_id,
            current_agent="triage",
        )
        self._sessions[session_id] = session
        await self._persist_session(session)
        return session

    async def get_session(self, session_id: str) -> SessionState | None:
        """Retrieve a session from memory, Redis (if available), or the database."""
        # Try in-memory first
        if session_id in self._sessions:
            return self._sessions[session_id]

        # Then Redis
        if _redis:
            try:
                data = await _redis.get(f"{_SESSION_KEY_PREFIX}{session_id}")
                if data:
                    obj = json.loads(data)
                    session = SessionState(**obj)
                    self._sessions[session_id] = session
                    return session
            except Exception as e:
                logger.warning("Redis session load failed: %s", e)

        # Finally the durable database layer
        return await self._load_from_db(session_id)

    async def _load_from_db(self, session_id: str) -> SessionState | None:
        if not db_enabled():
            return None
        try:
            async with AsyncSession() as db:
                state = await consultation_repo.load_session(db, session_id)
        except Exception as e:
            logger.warning("DB session load failed for %s: %s", session_id, e)
            return None
        if state:
            self._sessions[session_id] = state
        return state

    async def _persist_session(self, session: SessionState):
        """Save session to Redis and the database (both best-effort)."""
        if _redis:
            try:
                await _redis.setex(
                    f"{_SESSION_KEY_PREFIX}{session.session_id}",
                    _SESSION_TTL,
                    json.dumps(asdict(session), default=str),
                )
            except Exception as e:
                logger.warning("Redis session save failed: %s", e)
        if db_enabled():
            try:
                async with AsyncSession() as db:
                    await consultation_repo.save_session(db, session)
            except Exception as e:
                logger.warning(
                    "DB session save failed for %s: %s", session.session_id, e
                )
        # Always keep in-memory copy too for single-worker fallback
        self._sessions[session.session_id] = session

    async def run_agent(self, session: SessionState, user_input: str, llm_client=None) -> HandoverManifest:
        """Run the current agent with user input and return a manifest."""
        agent_cls = registry.get(session.current_agent)
        agent = agent_cls()

        # Hand the agent its own retrieval stack. ReviewAgent queries the KB
        # independently of the Doctor, so the "independent review" claim holds.
        if getattr(agent, "rag_query", None) is None and self.rag_query is not None:
            agent.rag_query = self.rag_query

        context = {
            **session.context,
            "symptoms": user_input,
            "messages": session.history[-10:] if session.history else [],
            "llm_client": llm_client,
        }

        # Hierarchical memory: inject the patient's profile and past visits so
        # returning patients don't repeat themselves. Best-effort — a memory
        # failure must never block the consultation.
        memory_block = await self._recall_memory(session.patient_id, user_input)
        if memory_block:
            context["patient_memory"] = memory_block

        # Pre-process hook (PII sanitization, emergency detection)
        processed = await agent.on_pre_process(context)

        # Run agent
        manifest = await agent.run(processed)

        # Post-process hook
        manifest = await agent.on_post_process(manifest)

        # Update session context with new info
        session.context.update(manifest.context)

        # Determine next agent
        next_agent = await self.route(session, session.context)
        session.current_agent = next_agent
        if next_agent == "emergency_protocol":
            # Emergency is a terminal state: the caller (main.py) emits the
            # "拨打 120" guidance and stops further conversation. Do NOT reset
            # current_agent back to triage here — that made every downstream
            # emergency_protocol check unreachable and let users keep chatting.
            manifest.risk_flags.insert(0, "EMERGENCY_PROTOCOL_ACTIVATED")

        # Add to history
        session.history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        session.history.append({
            "role": "agent",
            "agent": session.current_agent,
            "content": "\n".join(f"• {f}" for f in manifest.facts),
            "manifest": manifest.model_dump(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        await self._persist_session(session)
        await self._update_memory(session, manifest, next_agent)
        return manifest

    async def _recall_memory(self, patient_id: str, user_input: str) -> str:
        """Fetch the hierarchical memory block for a patient (best-effort)."""
        try:
            return await self.memory.retrieve(patient_id, user_input)
        except Exception as e:  # noqa: BLE001 - memory is an enhancement, not a gate
            logger.warning("Memory recall failed for %s: %s", patient_id, e)
            return ""

    async def _update_memory(
        self, session: SessionState, manifest: HandoverManifest, next_agent: str
    ) -> None:
        """Keep working memory in sync and archive finished consultations.

        Best-effort: a memory failure is logged and swallowed so the
        consultation itself is never affected.
        """
        try:
            await self.memory.set_current_agent(session.session_id, next_agent)
            await self.memory.update_context(session.session_id, {
                "current_agent": next_agent,
                "patient_id": session.patient_id,
            })
        except Exception as e:  # noqa: BLE001
            logger.warning("Working memory sync failed for %s: %s", session.session_id, e)

        # Archive the visit once the pipeline reaches a terminal state so the
        # next consultation can recall it (episodic memory).
        if next_agent not in ("complete", "emergency_protocol"):
            return

        assessment = self._extract_assessment(session)
        try:
            await self.memory.store_consultation(
                session.patient_id,
                session.session_id,
                assessment=assessment,
                status="emergency" if next_agent == "emergency_protocol" else "completed",
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("Episodic memory store failed for %s: %s", session.session_id, e)

    @staticmethod
    def _extract_assessment(session: SessionState) -> str:
        """Best-effort summary of a consultation for episodic recall."""
        for entry in reversed(session.history):
            if entry.get("role") != "agent":
                continue
            manifest = entry.get("manifest") or {}
            context = manifest.get("context") or {}
            for key in ("assessment", "diagnosis"):
                value = context.get(key)
                if isinstance(value, str) and value:
                    return value
                if isinstance(value, list) and value:
                    return "、".join(str(v) for v in value)
        return ""

    def cleanup_expired(self) -> int:
        """Remove in-memory sessions with no recent activity.

        Redis-backed sessions expire automatically via TTL; this only prunes
        the in-memory fallback store. Returns the number of sessions removed.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - _SESSION_TTL
        expired: list[str] = []
        for sid, session in self._sessions.items():
            last_ts = 0.0
            if session.history:
                raw = session.history[-1].get("timestamp", "")
                try:
                    last_ts = datetime.fromisoformat(raw).timestamp()
                except (ValueError, TypeError):
                    last_ts = 0.0
            if last_ts < cutoff:
                expired.append(sid)
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info("Cleaned up %d expired in-memory sessions", len(expired))
        return len(expired)


# ── Shared singleton ─────────────────────────────────────────────────────── #
# A single SupervisorAgent instance shared across the WebSocket endpoint
# (app.main) and the REST consultation API (app.api.consultation). This
# ensures both see the SAME in-memory session store even when Redis is not
# configured, so the review/summary pages can read the WS conversation.
supervisor = SupervisorAgent()
