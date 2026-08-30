from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="patient")  # patient | doctor
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
