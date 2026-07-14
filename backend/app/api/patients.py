"""Patient management API — CRUD endpoints.

All endpoints require authentication via the auth middleware.
Patient data is stored in-memory for demo mode; production uses PostgreSQL.
"""

import uuid
import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientListResponse,
)
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store (PostgreSQL in production)
_patients: dict[str, dict] = {}

# Seed demo patients
_demo_patients = [
    {
        "id": "patient_demo_001",
        "name": "张三",
        "gender": "男",
        "dob": date(1990, 5, 15),
        "phone": "138****5678",
        "allergies": ["青霉素"],
        "medical_history": ["高血压"],
        "created_at": "2026-06-01T08:00:00",
        "last_visit": "2026-06-20T14:30:00",
        "status": "active",
    },
    {
        "id": "patient_demo_002",
        "name": "李四",
        "gender": "女",
        "dob": date(1985, 8, 22),
        "phone": "139****4321",
        "allergies": [],
        "medical_history": ["哮喘"],
        "created_at": "2026-06-05T10:00:00",
        "last_visit": "2026-06-18T09:15:00",
        "status": "active",
    },
]
for p in _demo_patients:
    _patients[p["id"]] = p


def _compute_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _to_response(data: dict) -> PatientResponse:
    return PatientResponse(
        id=data["id"],
        name=data["name"],
        gender=data.get("gender"),
        dob=data.get("dob"),
        phone=data.get("phone"),
        age=_compute_age(data.get("dob")),
        allergies=data.get("allergies", []),
        medical_history=data.get("medical_history", []),
        created_at=data.get("created_at", ""),
        last_visit=data.get("last_visit"),
        status=data.get("status", "active"),
    )


@router.get("", response_model=PatientListResponse)
async def list_patients(
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user),
):
    """List patients with optional search."""
    items = list(_patients.values())
    if search:
        search_lower = search.lower()
        items = [p for p in items if search_lower in p["name"].lower()]

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]

    return PatientListResponse(
        total=total,
        items=[_to_response(p) for p in page_items],
    )


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    user_id: str = Depends(get_current_user),
):
    """Create a new patient record."""
    patient_id = f"patient_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "id": patient_id,
        "name": data.name,
        "gender": data.gender,
        "dob": data.dob,
        "phone": data.phone,
        "id_number": data.id_number,
        "address": data.address,
        "allergies": data.allergies or [],
        "medical_history": data.medical_history or [],
        "created_at": now,
        "last_visit": None,
        "status": "active",
    }
    _patients[patient_id] = record
    logger.info("Created patient: %s (by user=%s)", patient_id, user_id)
    return _to_response(record)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    user_id: str = Depends(get_current_user),
):
    """Get patient details by ID."""
    record = _patients.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"患者 {patient_id} 不存在")
    return _to_response(record)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    user_id: str = Depends(get_current_user),
):
    """Update patient information."""
    record = _patients.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"患者 {patient_id} 不存在")

    update_data = data.model_dump(exclude_unset=True)
    record.update(update_data)
    _patients[patient_id] = record
    logger.info("Updated patient: %s (by user=%s)", patient_id, user_id)
    return _to_response(record)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    user_id: str = Depends(get_current_user),
):
    """Delete a patient record."""
    if patient_id not in _patients:
        raise HTTPException(status_code=404, detail=f"患者 {patient_id} 不存在")
    del _patients[patient_id]
    logger.info("Deleted patient: %s (by user=%s)", patient_id, user_id)
    return {"message": f"患者 {patient_id} 已删除"}
