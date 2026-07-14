"""SupervisorAgent — manages session state and routes patients to the correct agent."""

import logging
from typing import Any

from agents.registry import registry
from app.schemas.agent import HandoverManifest
from orchestration.state import SessionState, GraphState

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Routes patients to the appropriate agent and manages the consultation flow.

    Responsibilities:
      - Determine the next agent based on triage result & conversation context
      - Maintain session state and history
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
                # Emergency cases bypass normal flow
                return "emergency_protocol"

            if department and department != "general":
                context["target_department"] = department

            return "doctor"

        elif current == "doctor":
            has_prescription = context.get("has_prescription", False) # 有处方需要review，没有处方可以直接跟进观察
            needs_review = context.get("needs_review", True)

            if needs_review and has_prescription:
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
        return session

    def get_session(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

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

        # Pre-process hook
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
            session.current_agent = "triage"  # stay on triage for emergency
            manifest.risk_flags.insert(0, "EMERGENCY_PROTOCOL_ACTIVATED")

        # Add to history
        from datetime import datetime, timezone

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

        return manifest

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
