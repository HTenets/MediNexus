from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, String

from .base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    phone = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    allergies = Column(JSON, default=list)
    medical_history = Column(JSON, default=list)
    last_visit = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
