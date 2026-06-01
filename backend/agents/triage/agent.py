"""TriageAgent — assesses symptoms and determines urgency, department, and info gaps."""

import json
import logging
from typing import Any

from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest
from agents.triage.prompt import TRIAGE_SYSTEM_PROMPT, TRIAGE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


@registry.register
class TriageAgent(BaseAgent):
    """Evaluates patient symptoms and produces a triage HandoverManifest."""

    def __init__(self):
        super().__init__("triage")

    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        """Analyze symptoms and return triage result."""
        symptoms = context.get("symptoms", "")
        patient_history = context.get("patient_history", "")
        messages = context.get("messages", [])

        # If an LLM client is available, use it for intelligent triage
        llm = context.get("llm_client")
        if llm:
            result = await self._llm_triage(llm, symptoms, patient_history, messages)
        else:
            # Fallback: keyword-based triage when no LLM is available
            result = self._keyword_triage(symptoms)

        facts = [
            f"Patient symptoms: {symptoms}",
            f"Urgency: {result.get('urgency', 'routine')}", # urgency 紧迫性，routine常规，urgent紧急，emergency危急
            f"Recommended department: {result.get('department', 'general')}",
            f"Reason: {result.get('reason', '')}",
        ]
        if patient_history:
            facts.append(f"History: {patient_history}")

        risk_flags = []
        if result.get("urgency") == "emergency":
            risk_flags.append("EMERGENCY_DETECTED")
        elif result.get("urgency") == "urgent":
            risk_flags.append("URGENT_CASE")

        return HandoverManifest(
            facts=facts,
            pending_questions=result.get("key_info_gaps", []),
            risk_flags=risk_flags,
            evidence_level="C", # TODO 这里的风险水平是写死的
            context={
                "triage_result": result,
                "department": result.get("department", ""),
                "urgency": result.get("urgency", "routine"),
            },
        )

    async def _llm_triage(self, llm, symptoms: str, history: str, messages: list[dict]) -> dict:
        """Use LLM for intelligent triage analysis."""
        user_message = f"Patient symptoms: {symptoms}\n"
        if history:
            user_message += f"Medical history: {history}\n"
        if messages:
            recent = messages[-3:] if len(messages) > 3 else messages
            user_message += f"Conversation history: {json.dumps(recent, ensure_ascii=False)}\n"

        system_prompt = TRIAGE_SYSTEM_PROMPT + "\n\n" + TRIAGE_EXTRACTION_PROMPT
        response = await llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ])

        try:
            parsed = json.loads(response)
            return {
                "urgency": parsed.get("urgency", "routine"),
                "department": parsed.get("department", ""),
                "reason": parsed.get("reason", ""),
                "key_info_gaps": parsed.get("key_info_gaps", []),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("LLM triage response parse failed: %s. Raw: %s", e, response)
            return self._keyword_triage(symptoms)

    def _keyword_triage(self, symptoms: str) -> dict:
        """Keyword-based fallback triage when no LLM is available."""
        text = symptoms.lower()

        # Emergency keywords
        emergency_kw = ["suicide", "自杀", "kill myself", "不想活", "chest pain", "胸痛",
                        "difficulty breathing", "呼吸困难", "unconscious", "昏迷",
                        "severe bleeding", "大出血", "severe allergic", "严重过敏",
                        "heart attack", "心脏病发作"]
        urgent_kw = ["high fever", "高烧", "severe pain", "剧痛", "fracture", "骨折",
                     "burn", "烧伤", "vomiting", "呕吐不止", "severe headache", "剧烈头痛"]

        for kw in emergency_kw:
            if kw in text:
                return {
                    "urgency": "emergency",
                    "department": "emergency",
                    "reason": f"Emergency keyword detected: {kw}",
                    "key_info_gaps": ["Time of onset", "Patient age", "Contact information"],
                }

        for kw in urgent_kw:
            if kw in text:
                return {
                    "urgency": "urgent",
                    "department": self._guess_department(text),
                    "reason": f"Urgent keyword detected: {kw}",
                    "key_info_gaps": ["Duration of symptoms", "Has the patient seen a doctor", "Medications taken"],
                }

        department = self._guess_department(text)
        return {
            "urgency": "routine",
            "department": department,
            "reason": f"Routine triage based on symptoms",
            "key_info_gaps": ["Duration of symptoms", "Severity (1-10)", "Any relevant medical history"],
        }

    def _guess_department(self, text: str) -> str:
        """Guess the department based on symptom keywords (bilingual)."""
        # 内科 / Internal Medicine
        if any(kw in text for kw in ["fever", "发烧", "cough", "咳嗽", "headache", "头痛",
                                      "dizziness", "头晕", "diarrhea", "腹泻", "nausea", "恶心",
                                      "hypertension", "高血压", "diabetes", "糖尿病",
                                      "cold", "感冒", "sore throat", "喉咙痛", "flu", "流感",
                                      "stomach", "胃", "腹部", "abdominal"]):
            return "internal_medicine"

        # 皮肤科 / Dermatology
        if any(kw in text for kw in ["rash", "皮疹", "itch", "痒", "skin", "皮肤",
                                      "acne", "痤疮", "eczema", "湿疹", "red spot", "红斑",
                                      "hives", "荨麻疹", "fungal", "真菌", "皮炎"]):
            return "dermatology"

        # 耳鼻喉科 / ENT
        if any(kw in text for kw in ["ear", "耳朵", "tinnitus", "耳鸣", "hearing", "听力",
                                      "nasal", "鼻塞", "runny nose", "流涕", "sinus", "鼻窦"]):
            return "ent"

        # 心理科 / Mental Health
        if any(kw in text for kw in ["anxiety", "anxious", "焦虑", "depression", "depressed", "抑郁",
                                      "insomnia", "失眠", "sleep", "sleeping", "stress", "压力",
                                      "panic", "惊恐", "mood", "情绪", "mental", "心理",
                                      "mental health", "精神", "trouble sleeping"]):
            return "mental_health"

        # 骨科 / Orthopedics
        if any(kw in text for kw in ["pain", "痛", "fracture", "骨折", "joint", "关节",
                                      "back", "背", "spine", "脊柱", "muscle", "肌肉",
                                      "swelling", "肿胀", "sprain", "扭伤"]):
            return "orthopedics"

        return "general"
