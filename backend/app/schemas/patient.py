from pydantic import BaseModel


class PatientResponse(BaseModel):
    id: str
    name: str
