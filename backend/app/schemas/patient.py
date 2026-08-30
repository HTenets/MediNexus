"""Patient Pydantic schemas."""

from datetime import date, datetime
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="患者姓名")
    gender: str | None = Field(None, pattern="^(男|女|other)$")
    dob: date | None = None
    phone: str | None = Field(None, pattern=r"^1[3-9]\d{9}$")
    id_number: str | None = Field(None, pattern=r"^\d{17}[\dXx]$")
    address: str | None = None
    allergies: list[str] = Field(default_factory=list, description="过敏史")
    medical_history: list[str] = Field(default_factory=list, description="既往史")


class PatientUpdate(BaseModel):
    name: str | None = None
    gender: str | None = Field(None, pattern="^(男|女|other)$")
    dob: date | None = None
    phone: str | None = Field(None, pattern=r"^1[3-9]\d{9}$")
    address: str | None = None
    allergies: list[str] | None = None
    medical_history: list[str] | None = None


class PatientResponse(BaseModel):
    id: str
    name: str
    gender: str | None = None
    dob: date | None = None
    phone: str | None = None
    age: int | None = None
    allergies: list[str] = []
    medical_history: list[str] = []
    created_at: str = ""
    last_visit: str | None = None
    status: str = "active"
    #: None for seeded demo patients visible to everyone; set for records the
    #: current user created (lets the UI tell "mine" from "sample data").
    owner_id: str | None = None


class PatientListResponse(BaseModel):
    total: int = 0
    items: list[PatientResponse] = []
