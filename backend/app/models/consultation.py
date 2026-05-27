from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped
from datetime import datetime, timezone
from .patient import Base


class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    status = Column(String, default="active")  # active | triaged | diagnosed | reviewed | completed
    diagnosis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
