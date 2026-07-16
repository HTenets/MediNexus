"""Consultation Pydantic schemas for request/response models."""

from pydantic import BaseModel
from typing import Any


class ConsultationStartRequest(BaseModel):
    patient_id: str | None = None
    symptoms: str = ""


class ConsultationStartResponse(BaseModel):
    session_id: str
    patient_id: str
    status: str
    current_agent: str
    created_at: str


class ConsultationStatusResponse(BaseModel):
    session_id: str
    patient_id: str = ""
    status: str = "active"
    current_agent: str = "triage"
    history: list[dict[str, Any]] = []


class SOAPCompletionRequest(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""
    diagnosis: str = ""


class ConsultationHistoryResponse(BaseModel):
    session_id: str
    records: list[dict[str, Any]] = []
    total: int = 0
