"""Follow-up scheduling logic."""
from dataclasses import dataclass
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
}
