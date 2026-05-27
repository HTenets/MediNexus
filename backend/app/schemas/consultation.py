from pydantic import BaseModel


class ConsultationRequest(BaseModel):
    patient_id: str
    symptoms: str


class ConsultationResponse(BaseModel):
    session_id: str
    status: str
