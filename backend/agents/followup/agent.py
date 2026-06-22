from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest
from datetime import datetime, timedelta, timezone
from agents.followup.scheduler import get_plan_for_diagnosis


@registry.register
class FollowupAgent(BaseAgent):
    """Manages post-visit follow-up scheduling and monitoring."""

    def __init__(self):
        super().__init__("followup")

    async def run(self, context: dict) -> HandoverManifest:
        diagnosis = context.get("diagnosis", {})
        possible_diagnoses = diagnosis.get("possible_diagnoses", []) if isinstance(diagnosis, dict) else []
        symptoms = context.get("symptoms", "")

        facts: list[str] = []
        pending_questions: list[str] = []
        risk_flags: list[str] = []

        if possible_diagnoses:
            primary = possible_diagnoses[0]
            dx_name = primary.get("diagnosis", "") if isinstance(primary, dict) else str(primary)
            likelihood = primary.get("likelihood", "") if isinstance(primary, dict) else ""

            # Determine plan type
            plan_type = get_plan_for_diagnosis(dx_name)
            plan_type_map = {
                "chronic_disease": "慢性病管理",
                "mental_health": "心理健康",
                "surgical": "术后随访",
                "routine": "常规随访",
            }
            plan_label = plan_type_map.get(plan_type, "常规随访")

            facts.append(f"诊断: {dx_name}")
            if likelihood:
                facts.append(f"可能性: {likelihood}")
            facts.append(f"随访类型: {plan_label}")

            if plan_type == "chronic_disease":
                facts.append("建议每30天定期复诊，监测病情变化")
                facts.append("慢性病需要长期管理，请遵医嘱用药")
            elif plan_type == "mental_health":
                facts.append("建议每2周复诊评估心理状态")
                facts.append("如有紧急情况请拨打心理援助热线")
            else:
                facts.append("建议1周后复诊，如症状加重请及时就医")
                facts.append("随访警示: 自限性疾病一般1周内可自愈，如持续加重请及时就诊")

            # Medication reminders
            treatment_plan = diagnosis.get("treatment_plan", {}) if isinstance(diagnosis, dict) else {}
            medications = treatment_plan.get("medications", []) if isinstance(treatment_plan, dict) else []
            if medications:
                med_names = [m.get("name", "") if isinstance(m, dict) else str(m) for m in medications]
                med_names = [n for n in med_names if n]
                if med_names:
                    facts.append(f"用药提醒: {'、'.join(med_names)} — 请按时按量服用")

            pending_questions.append("用药依从性如何？是否有漏服？")
            pending_questions.append("症状是否有所改善？")
            pending_questions.append("是否有药物不良反应？")

            if plan_type == "chronic_disease":
                pending_questions.append("血压/血糖监测记录如何？")

        else:
            facts.append(f"随访提醒: 针对症状「{symptoms}」建议观察")
            facts.append("如症状持续或加重，请及时复诊")
            pending_questions.append("症状是否缓解？")
            pending_questions.append("是否需要进一步检查？")

        facts.append("⚠️ 以上为AI生成的随访建议，仅供参考，不构成医疗诊断。如有不适请及时就医。")
        pending_questions.append("随访警示: 如出现呼吸困难、剧烈疼痛等紧急情况，请立即拨打120")

        return HandoverManifest(
            facts=facts,
            pending_questions=pending_questions,
            risk_flags=risk_flags,
        )

    async def schedule(self, patient_id: str, days_offset: int) -> dict:
        followup_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
        return {"patient_id": patient_id, "days_offset": days_offset, "scheduled_date": followup_date.isoformat()}
