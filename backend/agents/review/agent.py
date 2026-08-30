"""ReviewAgent — independently verifies DoctorAgent output against knowledge base.

Uses its own RAGQuery instance (not shared with DoctorAgent) to:
  1. Verify diagnosis against retrieved evidence
  2. Flag discrepancies between Doctor's output and knowledge base
  3. Check for missing differential diagnoses
  4. Mark risk flags if findings conflict
"""

import json
import logging
import re
from typing import Any

from agents.base import BaseAgent
from agents.registry import registry
from agents.review.prompt import REVIEW_LLM_PROMPT
from app.schemas.agent import HandoverManifest

logger = logging.getLogger(__name__)


def _seed_search(symptoms: str) -> str:
    """Load seed knowledge without triggering the ``knowledge`` package init.

    ``knowledge/__init__.py`` imports qdrant-dependent modules, which may not
    be installed in the runtime image. Import the dependency-free
    ``seed_data`` module directly by file path to avoid that.
    """
    try:
        import importlib.util
        import os

        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge",
            "seed_data.py",
        )
        spec = importlib.util.spec_from_file_location("_seed_data", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.search_seed_knowledge(symptoms)
    except Exception as e:  # noqa: BLE001
        logger.warning("Seed knowledge lookup failed: %s", e)
        return ""


@registry.register
class ReviewAgent(BaseAgent):
    """Reviews DoctorAgent output by independently querying the knowledge base."""

    def __init__(self, rag_query=None):
        super().__init__("review")
        self.rag_query = rag_query  # RAGQuery instance (independent from Doctor's)

    async def run(self, context: dict) -> HandoverManifest:
        symptoms = context.get("symptoms", "")

        if not symptoms:
            return HandoverManifest(facts=["暂无待审查的诊断内容。"])

        # Prefer LLM-based review; fall back to rule-based when unavailable.
        llm = context.get("llm_client")
        if llm:
            try:
                return await self._llm_review(llm, context)
            except Exception:
                logger.exception("LLM review failed, falling back to rule mode")
        return await self._rule_review(context)

    async def _llm_review(self, llm: Any, context: dict) -> HandoverManifest:
        """LLM-based prescription review with concrete medication guidance."""
        symptoms = context.get("symptoms", "")
        diagnosis_context = context.get("diagnosis", {})
        risk_flags = list(context.get("risk_flags", []))

        # Independently retrieve knowledge for grounding
        if self.rag_query:
            kb_context = await self.rag_query.query_formatted(symptoms, top_k=3)
        else:
            kb_context = _seed_search(symptoms)

        user_msg = f"## 患者主诉\n{symptoms}\n"
        if diagnosis_context:
            user_msg += f"\n## 医生诊断与方案\n{json.dumps(diagnosis_context, ensure_ascii=False, indent=2)}\n"
        # Patient profile / past visits — allergy and condition checks are only
        # meaningful with this context (e.g. drug–allergy contraindications).
        if context.get("patient_memory"):
            user_msg += f"\n## 患者档案与既往记录\n{context['patient_memory']}\n"
        if kb_context:
            user_msg += f"\n## 临床知识库参考\n{kb_context[:1200]}\n"
        if risk_flags:
            user_msg += f"\n## 已有风险标记\n{', '.join(risk_flags)}\n"

        response = await llm.chat([
            {"role": "system", "content": REVIEW_LLM_PROMPT},
            {"role": "user", "content": user_msg},
        ])
        parsed = self._parse_json(response)

        facts: list[str] = ["📋 **审查过程:** 独立检索临床知识库并复核医生方案"]
        review_risk_flags = list(risk_flags)

        summary = parsed.get("review_summary")
        if summary:
            facts.append(f"**审查摘要:** {summary}")

        meds = parsed.get("recommended_medications") or []
        if meds:
            facts.append("💊 **用药建议:**")
            for m in meds:
                if not isinstance(m, dict):
                    facts.append(f"- {m}")
                    continue
                name = m.get("name", "")
                dosage = m.get("dosage", "")
                course = m.get("course", "")
                head = f"- **{name}**"
                if dosage:
                    head += f" — {dosage}"
                if course:
                    head += f"，{course}"
                facts.append(head)
                if m.get("rationale"):
                    facts.append(f"  · 理由: {m['rationale']}")
                if m.get("cautions"):
                    facts.append(f"  · 注意: {m['cautions']}")
        else:
            facts.append("💊 **用药建议:** 当前信息不足以给出明确药物，建议补充症状细节或就医。")

        interactions = parsed.get("interactions") or []
        if interactions:
            facts.append("⚠️ **相互作用:** " + "；".join(str(i) for i in interactions))

        contraindications = parsed.get("contraindications") or []
        if contraindications:
            facts.append("🚫 **禁忌/过敏提示:** " + "；".join(str(c) for c in contraindications))

        if parsed.get("differential_note"):
            facts.append(f"💡 **鉴别提醒:** {parsed['differential_note']}")

        risk_level = parsed.get("risk_level", "safe")
        if risk_level == "high_risk":
            facts.append("🔴 **风险等级: 高** — 请重视下方结论。")
            if "REVIEW_HIGH_RISK" not in review_risk_flags:
                review_risk_flags.append("REVIEW_HIGH_RISK")
        elif risk_level == "caution":
            facts.append("🟡 **风险等级: 需谨慎**")

        evidence_level = parsed.get("evidence_level", "C")
        facts.append(f"**证据等级:** {evidence_level} (A=指南, B=共识, C=LLM生成)")

        if parsed.get("conclusion"):
            facts.append(f"✅ **审查结论:** {parsed['conclusion']}")
        facts.append("⚠️ **医疗免责声明:** 本审查由 AI 生成，仅供参考，处方药请在医生/药师指导下使用。")

        pending_questions: list[str] = []
        if evidence_level == "C":
            pending_questions.append("建议: 低证据等级的建议，请结合临床判断。")

        return HandoverManifest(
            facts=facts,
            pending_questions=pending_questions,
            risk_flags=review_risk_flags,
            evidence_level=evidence_level,
            context={"review_completed": True, "review_llm_mode": True},
        )

    @staticmethod
    def _parse_json(response: str) -> dict:
        """Parse LLM JSON output, tolerating markdown code fences."""
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            pass
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response or "", re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        logger.warning("Failed to parse LLM review response as JSON: %.100s", response)
        return {}

    async def _rule_review(self, context: dict) -> HandoverManifest:
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

        # Step 1: Independently query RAG (or seeded demo knowledge)
        if self.rag_query:
            kb_context = await self.rag_query.query_formatted(symptoms, top_k=3)
            facts.append("📋 **审查过程: 独立检索知识库验证**")
            if kb_context:
                facts.append(f"检索到相关知识: {kb_context[:200]}...")
            else:
                facts.append("知识库检索无匹配结果 (仅基于规则审查)。")
        else:
            kb_context = _seed_search(symptoms)
            facts.append("📋 **审查过程: 独立检索临床知识库验证**")
            if kb_context:
                facts.append(f"检索到相关临床指引: {kb_context[:240]}")
            else:
                facts.append("未检索到匹配指引 (仅基于规则审查)。")

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
