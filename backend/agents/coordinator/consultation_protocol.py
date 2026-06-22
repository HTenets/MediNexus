"""Consultation protocol — state machine and data structures."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class ConsultationPhase:
    INIT = "init"
    SPECIALISTS_INVITED = "specialists_invited"
    OPINIONS_COLLECTED = "opinions_collected"
    CONSENSUS_REACHED = "consensus_reached"
    COMPLETED = "completed"


@dataclass
class SpecialistOpinion:
    specialty: str
    diagnosis: list[str] = field(default_factory=list)
    confidence: float = 0.5
    evidence_level: str = "C"
    recommendations: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ConsultationReport:
    session_id: str
    patient_id: str
    chief_complaint: str
    specialties_involved: list[str]
    opinions: list[SpecialistOpinion] = field(default_factory=list)
    consensus_diagnosis: list[str] = field(default_factory=list)
    consensus_plan: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.completed_at:
            self.completed_at = datetime.utcnow().isoformat()
