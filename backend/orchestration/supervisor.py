"""SupervisorAgent — manages session state and routes patients to the correct agent.

Sessions are stored in-memory by default. When REDIS_URL is configured,
sessions are serialized to Redis so they persist across restarts and are
shared across multiple Uvicorn workers.
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from agents.registry import registry
from app.config import settings
from app.schemas.agent import HandoverManifest
from orchestration.state import SessionState, GraphState

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

    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

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

    async def create_session(self, session_id: str, patient_id: str) -> SessionState:
        """Create a new consultation session."""
        session = SessionState(
            session_id=session_id,
            patient_id=patient_id,
            current_agent="triage",
        )
        self._sessions[session_id] = session
        await self._persist_session(session)
        return session

    async def get_session(self, session_id: str) -> SessionState | None:
        """Retrieve a session from Redis (if available) or in-memory store."""
        # Try Redis first
        if _redis:
            try:
                data = await _redis.get(f"{_SESSION_KEY_PREFIX}{session_id}")
                if data:
                    obj = json.loads(data)
                    return SessionState(**obj)
            except Exception as e:
                logger.warning("Redis session load failed: %s", e)

        # Fall back to in-memory
        return self._sessions.get(session_id)

    async def _persist_session(self, session: SessionState):
        """Save session to Redis (if available)."""
        if _redis:
            try:
                await _redis.setex(
                    f"{_SESSION_KEY_PREFIX}{session.session_id}",
                    _SESSION_TTL,
                    json.dumps(asdict(session), default=str),
                )
            except Exception as e:
                logger.warning("Redis session save failed: %s", e)
        # Always keep in-memory copy too for single-worker fallback
        self._sessions[session.session_id] = session

    async def run_agent(self, session: SessionState, user_input: str, llm_client=None) -> HandoverManifest:
        """Run the current agent with user input and return a manifest."""
        agent_cls = registry.get(session.current_agent)
        agent = agent_cls()

        context = {
            **session.context,
            "symptoms": user_input,
            "messages": session.history[-10:] if session.history else [],
            "llm_client": llm_client,
        }

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
            session.current_agent = "triage"
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
        return manifest

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

    def session_to_graph_state(self, session: SessionState) -> GraphState:
        """Convert a SessionState to a LangGraph-compatible GraphState TypedDict."""
        return GraphState(
            session_id=session.session_id,
            patient_id=session.patient_id,
            current_agent=session.current_agent,
            messages=session.history,
            context=session.context,
            pending_questions=[],
            risk_flags=[],
            evidence_level="C",
            agent_output=None,
            error=None,
        )


# ── Shared singleton ─────────────────────────────────────────────────────── #
# A single SupervisorAgent instance shared across the WebSocket endpoint
# (app.main) and the REST consultation API (app.api.consultation). This
# ensures both see the SAME in-memory session store even when Redis is not
# configured, so the review/summary pages can read the WS conversation.
supervisor = SupervisorAgent()
