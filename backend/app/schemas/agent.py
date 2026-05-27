from pydantic import BaseModel
from typing import Any


class HandoverManifest(BaseModel):
    facts: list[str] = []
    pending_questions: list[str] = []
    risk_flags: list[str] = []
    evidence_level: str = "C"  # A: guideline指南, B: consensus共识, C: LLM-generated
    context: dict[str, Any] = {}
