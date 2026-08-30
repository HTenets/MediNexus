from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from .base import Base


class Followup(Base):
    __tablename__ = "followups"
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    consultation_id = Column(String, ForeignKey("consultations.id"), nullable=False)
    status = Column(String, default="pending")  # pending | completed | cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
