from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from .base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(String, primary_key=True)
    consultation_id = Column(String, ForeignKey("consultations.id"), nullable=False)
    content = Column(Text, nullable=False)
    review_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
