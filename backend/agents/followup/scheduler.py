"""Follow-up scheduling logic."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class FollowupPlan:
    patient_id: str
    interval_days: int
    total_visits: int


DEFAULT_PLANS: dict[str, FollowupPlan] = {
    "chronic_disease": FollowupPlan("", 30, 6),
    "post_surgery": FollowupPlan("", 7, 4),
    "medication_monitoring": FollowupPlan("", 14, 3),
    "mental_health": FollowupPlan("", 14, 8),
    "routine": FollowupPlan("", 7, 1),
}


@dataclass
class ScheduledFollowup:
    patient_id: str
    consultation_id: str
    visit_number: int
    scheduled_date: str
    status: str = "pending"


def get_plan_for_diagnosis(diagnosis: str) -> str:
    """Map a diagnosis to a follow-up plan type."""
    chronic_keywords = ["高血压", "糖尿病", "冠心病", "慢性", "chronic", "hypertension", "diabetes"]
    mental_keywords = ["焦虑", "抑郁", "失眠", "anxiety", "depression", "insomnia"]
    surgical_keywords = ["术后", "surgery", "post-op"]

    dx_lower = diagnosis.lower()
    for kw in chronic_keywords:
        if kw in dx_lower:
            return "chronic_disease"
    for kw in mental_keywords:
        if kw in dx_lower:
            return "mental_health"
    for kw in surgical_keywords:
        if kw in dx_lower:
            return "post_surgery"
    return "routine"


def generate_schedule(patient_id: str, consultation_id: str, plan_type: str) -> list[ScheduledFollowup]:
    """Generate a list of scheduled follow-ups based on plan type."""
    plan = DEFAULT_PLANS.get(plan_type, DEFAULT_PLANS["routine"])
    schedule: list[ScheduledFollowup] = []
    base_date = datetime.utcnow()

    for i in range(plan.total_visits):
        visit_date = base_date + timedelta(days=plan.interval_days * (i + 1))
        schedule.append(ScheduledFollowup(
            patient_id=patient_id,
            consultation_id=consultation_id,
            visit_number=i + 1,
            scheduled_date=visit_date.isoformat(),
        ))

    return schedule
