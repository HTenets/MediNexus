"""DoctorAgent — 执行医疗诊断并集成专科技能。

流程:
  1. 接收分诊结果 (科室, 紧急程度)
  2. 自动选择匹配的专科 Skill
  3. 将 Skill 的 system_prompt + 知识注入 LLM 上下文
  4. 运行诊断状态机 (INITIAL → DIFFERENTIAL → TREATMENT → COMPLETED)
  5. 当 LLM 不可用时回退到基于规则的推荐

DoctorAgent — performs medical diagnosis with specialty Skill integration.

Flow:
  1. Receives triage results (department, urgency)
  2. Auto-selects the matching specialty Skill
  3. Injects Skill system_prompt + knowledge into LLM context
  4. Runs through diagnosis state machine (INITIAL → DIFFERENTIAL → TREATMENT → COMPLETED)
  5. Falls back to rule-based recommendations when LLM is unavailable

"""

import json
import logging
import re
from typing import Any

from agents.base import BaseAgent
from agents.doctor.diagnosis_flow import DiagnosisState
from agents.doctor.prompt import DIAGNOSIS_SYSTEM_PROMPT
from agents.doctor.skills.registry import registry as skill_registry
from agents.doctor.skills.loader import load_builtin_skills
from agents.registry import registry as agent_registry
from app.schemas.agent import HandoverManifest

logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = (
    "⚠️ **医疗免责声明**\n\n"
    "本回答由 AI 生成, 仅供参考, 不构成医疗诊断建议。\n"
    "如有身体不适, 请及时前往正规医疗机构就诊。\n"
    "如遇紧急情况, 请立即拨打 120 急救电话。"
)


def _merge_memory(patient_history: str, memory_block: str) -> str:
    """Combine caller-supplied history with the hierarchical memory block."""
    history = (patient_history or "").strip()
    memory = (memory_block or "").strip()
    if history and memory:
        return f"{history}\n\n{memory}"
    return history or memory


@agent_registry.register
class DoctorAgent(BaseAgent):
    """Performs medical diagnosis with specialty Skill selection and LLM/rule dual-mode."""

    def __init__(self):
        super().__init__("doctor")
        self._skills_loaded = False

    def _ensure_skills(self):
        """Lazy-load builtin skills on first use."""
        if not self._skills_loaded:
            load_builtin_skills()
            self._skills_loaded = True

    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        self._ensure_skills()

        # Extract context
        symptoms = context.get("symptoms", "")
        department = context.get("department", "")
        urgency = context.get("urgency", "routine")
        messages = context.get("messages", [])
        patient_history = context.get("patient_history", "")
        current_state = context.get("diagnosis_state", DiagnosisState.INITIAL)

        # Hierarchical memory (patient profile + past visits) supplied by the
        # supervisor. Folded into the history block so both the LLM and the
        # rule-based path see it.
        patient_history = _merge_memory(patient_history, context.get("patient_memory", ""))

        if not symptoms.strip():
            return HandoverManifest(
                facts=["请描述您的症状, 以便我为您提供诊断建议。"],
                pending_questions=["您的主要症状是什么?", "症状持续了多久?", "还有其他不适吗?"],
                evidence_level="C",
            )

        # Auto-select skill based on triage info or symptom matching
        skill = await skill_registry.auto_route(symptoms, department)
        if skill:
            logger.info("DoctorAgent selected skill: %s for department=%s", skill.name, department)
        else:
            logger.info("DoctorAgent: no matching skill found, using general diagnosis")

        # Choose diagnosis mode based on LLM availability
        llm = context.get("llm_client")
        if llm:
            return await self._llm_diagnose(llm, symptoms, skill, current_state, patient_history, messages, urgency)
        else:
            return self._rule_diagnose(symptoms, skill, current_state, patient_history, urgency)

    async def _llm_diagnose(
        self,
        llm: Any,
        symptoms: str,
        skill: Any,
        state: str,
        patient_history: str,
        messages: list[dict],
        urgency: str,
    ) -> HandoverManifest:
        """LLM-based diagnosis with Skill context injection."""
        # Build system prompt from skill
        system_parts = []
        if skill and skill.system_prompt:
            system_parts.append(skill.system_prompt)
        else:
            system_parts.append(DIAGNOSIS_SYSTEM_PROMPT)

        # Inject skill-specific knowledge
        if skill:
            try:
                knowledge = await skill.get_knowledge({"symptoms": symptoms, "patient_history": patient_history})
                if knowledge:
                    system_parts.append(f"\n## 专科知识参考\n{knowledge}")
            except Exception as e:
                logger.warning("Skill knowledge retrieval failed: %s", e)

        system_prompt = "\n\n".join(system_parts)

        # Build user message
        user_msg = f"## 患者主诉\n{symptoms}\n"
        if patient_history:
            user_msg += f"\n## 既往病史\n{patient_history}\n"
        if urgency == "emergency":
            user_msg += "\n⚠️ **紧急情况标记**: 请优先评估是否需要立即急救。\n"
        elif urgency == "urgent":
            user_msg += "\n⚠️ **加急标记**: 建议尽快处理。\n"

        # Include recent conversation context
        if messages:
            recent = messages[-5:] if len(messages) > 5 else messages
            user_msg += f"\n## 对话历史\n{json.dumps(recent, ensure_ascii=False, indent=2)}\n"

        user_msg += (
            "\n请按以下JSON格式输出诊断结果:\n"
            '{"analysis": {"possible_diagnoses": [...], "treatment_plan": {...}}, '
            '"red_flags": [...], "pending_questions": [...]}'
        )

        try:
            response = await llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ])

            parsed = self._parse_diagnosis_response(response)
            facts = self._build_facts(parsed, symptoms, skill)
            risk_flags = []
            if urgency == "emergency":
                risk_flags.append("EMERGENCY_DETECTED")
            if parsed.get("red_flags"):
                risk_flags.extend(parsed["red_flags"])

            return HandoverManifest(
                facts=facts,
                pending_questions=parsed.get("pending_questions", []),
                risk_flags=risk_flags,
                evidence_level="C",
                context={
                    "diagnosis": parsed,
                    "diagnosis_state": DiagnosisState.COMPLETED,
                    "skill_used": skill.name if skill else None,
                    "llm_mode": True,
                    "has_prescription": bool(parsed.get("treatment_plan")),
                },
            )

        except Exception as e:
            logger.exception("LLM diagnosis failed, falling back to rule mode")
            return self._rule_diagnose(symptoms, skill, state, patient_history, urgency)

    def _rule_diagnose(
        self,
        symptoms: str,
        skill: Any,
        state: str,
        patient_history: str,
        urgency: str,
    ) -> HandoverManifest:
        """Rule-based fallback diagnosis when LLM is unavailable."""
        text = symptoms.lower()

        facts = ["[模式: 规则引擎] 当前为离线降级模式, 建议配置 LLM Key 获得完整体验"]
        risk_flags = []
        pending_questions = [
            "症状持续了多久?",
            "疼痛/不适程度 (1-10分)?",
            "是否有其他伴随症状?",
            "是否有相关既往病史?",
        ]

        # Urgency-based facts
        if urgency == "emergency":
            facts.append("⚠️ 检测到紧急情况信号, 请立即拨打 120 或前往急诊就医。")
            risk_flags.append("EMERGENCY_DETECTED")
            return HandoverManifest(facts=facts, pending_questions=[], risk_flags=risk_flags, evidence_level="C")

        elif urgency == "urgent":
            facts.append("⚠️ 建议您尽快就医, 不要拖延。")
            pending_questions.insert(0, "是否已经去过医院? 医生怎么说?")

        # Department-specific fallback
        if skill and skill.name == "internal_medicine":
            self._add_internal_medicine_facts(text, facts, pending_questions)
        elif skill and skill.name == "dermatology":
            self._add_dermatology_facts(text, facts, pending_questions)
        elif skill and skill.name == "ent":
            self._add_ent_facts(text, facts, pending_questions)
        elif skill and skill.name == "mental_health":
            self._add_mental_health_facts(text, facts, pending_questions)
        else:
            self._add_general_facts(text, facts, pending_questions)

        # Also consider exact symptom matches for any skill
        if not skill or skill.name not in ("internal_medicine", "dermatology", "ent", "mental_health"):
            self._add_symptom_specific_facts(text, facts)

        facts.append(MEDICAL_DISCLAIMER)

        return HandoverManifest(
            facts=facts,
            pending_questions=pending_questions,
            risk_flags=risk_flags,
            evidence_level="C",
            context={
                "diagnosis_state": DiagnosisState.INITIAL,
                "skill_used": skill.name if skill else None,
                "llm_mode": False,
                "has_prescription": True,
            },
        )

    # ------------------------------------------------------------------ #
    #  Rule-based fact builders (organized by department)
    #  基于规则的事实构建器（按部门组织）
    # ------------------------------------------------------------------ #

    def _add_internal_medicine_facts(self, text: str, facts: list, questions: list):
        if any(kw in text for kw in ["fever", "发烧", "cough", "咳嗽", "cold", "感冒", "flu", "流感"]):
            facts.append("常见病因: 上呼吸道感染(感冒/流感)可能性较大。")
            facts.append("建议: 多休息、多饮水, 体温超过38.5°C可考虑退热药(对乙酰氨基酚)。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["是否有咳痰? 痰的颜色?", "有无呼吸困难?"])
        elif any(kw in text for kw in ["stomach", "胃", "abdominal", "腹部", "diarrhea", "腹泻"]):
            facts.append("常见病因: 急性胃肠炎可能性较大。")
            facts.append("建议: 注意饮食清淡, 补充水分和电解质, 避免油腻辛辣食物。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["大便性状和频率?", "有无发热?", "有无不洁饮食史?"])
        elif any(kw in text for kw in ["头", "head", "头痛", "dizziness", "头晕"]):
            facts.append("头痛/头晕的常见原因包括: 紧张性头痛、偏头痛、感冒、睡眠不足、血压异常。")
            facts.append("建议: 注意休息, 监测血压, 避免过度用眼。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["头痛部位和性质(胀痛/跳痛/刺痛)?", "有无恶心呕吐?", "有无视力改变?"])
        else:
            facts.append("建议: 内科常见疾病请提供更多具体症状以便判断。")
            facts.append("请关注体温、疼痛部位、消化系统症状等关键信息。")

    def _add_dermatology_facts(self, text: str, facts: list, questions: list):
        if any(kw in text for kw in ["itch", "痒", "rash", "皮疹"]):
            facts.append("皮肤瘙痒/皮疹的常见原因: 湿疹、荨麻疹、接触性皮炎、过敏性皮炎。")
            facts.append("建议: 避免搔抓, 保持皮肤清洁干燥, 可使用温和的外用止痒药膏。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["皮疹的具体形态(红斑/丘疹/水疱)?", "出现多久了?", "有无接触过新的物品/食物?"])
        elif any(kw in text for kw in ["acne", "痤疮", "痘痘"]):
            facts.append("痤疮(青春痘)常见于青少年和青年, 与激素水平、皮脂分泌过多有关。")
            facts.append("建议: 保持面部清洁, 避免挤压, 可使用含有水杨酸或过氧化苯甲酰的护肤品。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["痤疮的严重程度(少量粉刺/炎性丘疹/结节囊肿)?", "是否在经期前后加重?"])
        else:
            facts.append("建议: 皮肤科疾病请描述皮损的具体形态、部位、伴随症状。")

    def _add_ent_facts(self, text: str, facts: list, questions: list):
        if any(kw in text for kw in ["sore throat", "咽痛", "喉咙痛", "扁桃体"]):
            facts.append("咽喉痛常见原因: 急性咽炎/扁桃体炎(病毒性或细菌性)。")
            facts.append("建议: 温盐水漱口、多饮温水、避免刺激性食物。如有发热可考虑退热药。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["有无发热? 体温多少?", "吞咽时疼痛是否加剧?", "有无扁桃体肿大或脓点?"])
        elif any(kw in text for kw in ["ear", "耳朵", "耳鸣", "tinnitus"]):
            facts.append("耳部不适的常见原因: 外耳道炎、中耳炎、耵聍栓塞、耳鸣。")
            facts.append("建议: 避免用棉签掏耳, 保持耳道干燥。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["耳痛还是听力下降?", "有无耳漏(流脓/流水)?", "有无眩晕?"])
        elif any(kw in text for kw in ["鼻", "nasal", "sinus", "鼻窦"]):
            facts.append("鼻部不适常见原因: 过敏性鼻炎、急性鼻窦炎、感冒。")
            facts.append("建议: 生理盐水洗鼻, 避免接触过敏原。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["流清涕还是脓涕?", "有无面部压痛?", "有无喷嚏和眼痒?"])
        else:
            facts.append("建议: 耳鼻喉科疾病请描述具体部位(耳/鼻/咽喉)和症状。")

    def _add_mental_health_facts(self, text: str, facts: list, questions: list):
        suicide_detected = any(kw in text for kw in ["suicide", "自杀", "kill myself", "不想活", "end my life"])
        if suicide_detected:
            facts.append("⚠️ 检测到可能与自杀相关的描述。请立即寻求专业帮助!")
            facts.append("📞 心理危机热线: 400-161-9995 (中国24小时)")
            facts.append("📞 北京心理危机干预中心: 010-82951332")
            facts.append("📞 全国希望热线: 400-161-9995")
            facts.clear()  # Replace all facts with crisis info
            facts.append("【危机干预信息】检测到紧急心理危机信号, 请立即拨打心理援助热线。")
            facts.append("您的生命非常宝贵, 请给专业人员一个帮助您的机会。")
            return

        if any(kw in text for kw in ["anxiety", "焦虑", "紧张", "worry", "担心", "panic", "惊恐"]):
            facts.append("焦虑症状常见表现: 紧张不安、过度担忧、心慌、手抖、失眠。")
            facts.append("建议: 深呼吸放松练习, 规律运动, 减少咖啡因摄入。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["这种焦虑感持续多久了?", "有没有特定的诱因?", "是否影响日常工作生活?"])
        elif any(kw in text for kw in ["depress", "抑郁", "低落", "sad", "悲伤", "绝望"]):
            facts.append("情绪低落的常见原因: 生活压力、人际关系问题、季节性情绪变化。")
            facts.append("建议: 保持规律作息, 适度运动, 与信任的人交流感受。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend([
                "这种情绪持续多久了? (超过2周需要注意)",
                "对以前喜欢的事情还有兴趣吗?",
                "睡眠和胃口有变化吗?",
            ])
        elif any(kw in text for kw in ["失眠", "insomnia", "sleep", "睡"]):
            facts.append("睡眠问题常见原因: 压力、焦虑、不规律的作息、咖啡因/酒精。")
            facts.append("建议: 固定作息时间, 睡前1小时减少屏幕使用, 卧室保持凉爽黑暗。")
            facts.append("证据等级: C (LLM 经验性建议)")
            questions.extend(["是入睡困难还是容易早醒?", "每晚大约睡几个小时?", "白天是否影响精神状态?"])
        else:
            facts.append("建议: 心理科常见问题包括情绪困扰、压力管理、睡眠问题。")
            questions.extend(["您最困扰的症状是什么?", "这种情况持续多久了?", "对日常生活有多大影响?"])

    def _add_general_facts(self, text: str, facts: list, questions: list):
        facts.append("请提供更详细的症状描述, 以便我为您匹配最合适的科室。")
        questions.append("您的主要不适部位是哪里?")

    def _add_symptom_specific_facts(self, text: str, facts: list):
        """Catch-all: try to identify body regions from symptom text."""
        if any(kw in text for kw in ["chest", "胸", "heart", "心"]):
            facts.append("胸部不适请警惕心血管问题, 尤其伴出汗、呼吸困难时。")
        elif any(kw in text for kw in ["back", "背", "腰", "spine", "脊柱"]):
            facts.append("腰背部疼痛常见于肌肉劳损、腰椎问题。建议注意休息, 避免负重。")

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _parse_diagnosis_response(self, response: str) -> dict:
        """Parse LLM JSON response with fallback for malformed (格式错误的) output."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        # Try to extract JSON from markdown code block
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Fallback: return raw text as a fact
        logger.warning("Failed to parse LLM diagnosis response as JSON: %.100s", response)
        return {"possible_diagnoses": [], "treatment_plan": {}, "red_flags": [], "pending_questions": []}

    def _build_facts(self, parsed: dict, symptoms: str, skill: Any) -> list[str]:
        """Build human-readable facts list from parsed diagnosis."""
        facts = [f"患者主诉: {symptoms}"]

        diagnoses = parsed.get("possible_diagnoses", [])
        if diagnoses:
            if isinstance(diagnoses, list):
                facts.append("**可能的诊断:**")
                for dx in diagnoses:
                    if isinstance(dx, dict):
                        name = dx.get("diagnosis", str(dx))
                        likelihood = dx.get("likelihood", "")
                        reason = dx.get("reason", "")
                        line = f"- {name}"
                        if likelihood:
                            line += f" ({likelihood})"
                        facts.append(line)
                        if reason:
                            facts.append(f"  依据: {reason}")
                    else:
                        facts.append(f"- {dx}")
            else:
                facts.append(f"可能的诊断: {diagnoses}")
        else:
            facts.append("正在分析症状, 请回答追问以便更准确判断。")

        treatment = parsed.get("treatment_plan", {})
        if treatment:
            facts.append("")
            facts.append("**建议:**")
            if isinstance(treatment, dict):
                for key, val in treatment.items():
                    if isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                facts.append(f"- {item.get('name', '')} ({item.get('dosage', '')}) [{item.get('evidence_level', 'C')}]")
                            else:
                                facts.append(f"- {item}")
                    elif isinstance(val, str) and val:
                        facts.append(f"- {key}: {val}")
            else:
                facts.append(f"- {treatment}")

        return facts
