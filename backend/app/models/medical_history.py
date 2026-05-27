from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from datetime import datetime, timezone
from .patient import Base


class MedicalHistory(Base):
    __tablename__ = "medical_histories"
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    history_type = Column(String)  # allergy | past_illness | family | medication
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
