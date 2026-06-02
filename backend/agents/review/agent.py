from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest


@registry.register
class ReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("review")

    async def run(self, context: dict) -> HandoverManifest:
        return HandoverManifest(
            facts=context.get("facts", []),
            pending_questions=[],
            risk_flags=context.get("risk_flags", []),
            evidence_level="B",
        )
