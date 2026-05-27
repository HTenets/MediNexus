from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest


class TriageAgent(BaseAgent):
    def __init__(self):
        super().__init__("triage")

    async def run(self, context: dict) -> HandoverManifest:
        return HandoverManifest(
            facts=[f"Symptoms: {context.get('symptoms', '')}"],
            pending_questions=["Specialty determination"],
            risk_flags=[],
        )
