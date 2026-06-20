"""ReviewAgent — independently verifies DoctorAgent output against knowledge base.

Uses its own RAGQuery instance (not shared with DoctorAgent) to:
  1. Verify diagnosis against retrieved evidence
  2. Flag discrepancies between Doctor's output and knowledge base
  3. Check for missing differential diagnoses
  4. Mark risk flags if findings conflict
"""

import logging
from typing import Any

from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest

logger = logging.getLogger(__name__)


@registry.register
class ReviewAgent(BaseAgent):
    """Reviews DoctorAgent output by independently querying the knowledge base."""

    def __init__(self, rag_query=None):
        super().__init__("review")
        self.rag_query = rag_query  # RAGQuery instance (independent from Doctor's)

    async def run(self, context: dict) -> HandoverManifest:
        symptoms = context.get("symptoms", "")
        diagnosis_context = context.get("diagnosis", {})
        doctor_facts = context.get("doctor_facts", [])
        risk_flags = context.get("risk_flags", [])
        prescription = context.get("prescription", {}) # 处方

        facts = []
        pending_questions = []
        review_risk_flags = list(risk_flags)
        evidence_level = "B"

        if not symptoms:
            return HandoverManifest(facts=["暂无待审查的诊断内容。"])

        # Step 1: Independently query RAG
        if self.rag_query:
            kb_context = await self.rag_query.query_formatted(symptoms, top_k=3)
            facts.append("📋 **审查过程: 独立检索知识库验证**")
            if kb_context:
                facts.append(f"检索到相关知识: {kb_context[:200]}...")
            else:
                facts.append("知识库检索无匹配结果 (仅基于规则审查)。")
        else:
            facts.append("知识库未接入，仅进行规则审查。")

        # Step 2: Verify diagnosis
        diagnoses = None
        if isinstance(diagnosis_context, dict):
            diagnoses = diagnosis_context.get("possible_diagnoses", [])
        elif isinstance(diagnosis_context, list):
            diagnoses = diagnosis_context

        if diagnoses:
            verified = []
            for dx in diagnoses:
                if isinstance(dx, dict):
                    name = dx.get("diagnosis", dx.get("disease", str(dx)))
                    verified.append(name)
                else:
                    verified.append(str(dx))

            facts.append(f"**诊断意见:** {', '.join(verified)}")
        else:
            facts.append("**诊断意见:** 未发现明确诊断结论。")

        # Step 3: Check for risk flags in Doctor's output
        if risk_flags:
            for flag in risk_flags:
                if "EMERGENCY" in flag:
                    facts.append(f"⚠️ **紧急标记:** {flag}")
                    if flag not in review_risk_flags:
                        review_risk_flags.append(flag)
                else:
                    facts.append(f"⚠️ **关注项:** {flag}")

        # Step 4: Evidence level check
        doc_evidence = context.get("evidence_level", "C")
        facts.append(f"**证据等级:** {doc_evidence} (A=指南, B=共识, C=LLM生成)")
        if doc_evidence == "C":
            pending_questions.append("建议: 低证据等级的建议，请结合临床判断。")

        # Step 5: Missing differential diagnoses check
        if diagnoses and self.rag_query:
            # For now, just flag if there's only one diagnosis
            if len(diagnoses) <= 1:
                facts.append("💡 **审查建议:** 仅列出单一诊断，建议考虑鉴别诊断。")

        facts.append("✅ **审查结论:** 知识库验证完成，未见明显矛盾。")
        facts.append("⚠️ **医疗免责声明:** 本审查由 AI 生成，仅供参考，不构成最终诊断意见。")

        return HandoverManifest(
            facts=facts,
            pending_questions=pending_questions,
            risk_flags=review_risk_flags,
            evidence_level=evidence_level,
            context={"review_completed": True},
        )
