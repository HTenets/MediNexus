from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text

from .base import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(String, primary_key=True)
    # No FK to patients: sessions may reference ad-hoc patient ids that are
    # not (yet) registered patient records.
    patient_id = Column(String, nullable=False, index=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String, default="active")  # active | completed | emergency
    current_agent = Column(String, default="triage")
    history = Column(JSON, default=list)
    context = Column(JSON, default=dict)
    diagnosis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
