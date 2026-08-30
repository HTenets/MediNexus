from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from .base import Base


class MedicalRecord(Base):
    """SOAP-style visit record attached to a patient."""

    __tablename__ = "medical_records"

    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    subjective = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    department = Column(String, nullable=True)
    doctor = Column(String, nullable=True)
