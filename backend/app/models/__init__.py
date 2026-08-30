"""ORM models — importing this package registers all tables on Base.metadata."""

from .base import Base
from .user import User
from .patient import Patient
from .consultation import Consultation
from .medical_record import MedicalRecord
from .prescription import Prescription
from .medical_history import MedicalHistory
from .followup import Followup
from .audit_log import AuditLog

__all__ = [
    "Base",
    "User",
    "Patient",
    "Consultation",
    "MedicalRecord",
    "Prescription",
    "MedicalHistory",
    "Followup",
    "AuditLog",
]
