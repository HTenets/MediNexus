"""Patient management API — CRUD endpoints.

All endpoints require authentication via the auth middleware.
When a database is configured, patients are persisted in PostgreSQL;
otherwise an in-memory store keeps the zero-setup demo working.
"""

import uuid
import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Depends

from app.models import Patient
from app.repositories import patient_repo
from app.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientListResponse,
)
from app.core.auth import get_current_user
from app.core.database import AsyncSession, db_enabled

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory fallback store (used only when no database is configured)
_patients: dict[str, dict] = {}

_demo_patients = [
    {
        "id": "patient_demo_001",
        "name": "张三",
        "gender": "男",
        "dob": date(1990, 5, 15),
        "phone": "13800005678",
        "allergies": ["青霉素"],
        "medical_history": ["高血压"],
        "created_at": "2026-06-01T08:00:00+00:00",
        "last_visit": "2026-06-20T14:30:00+00:00",
        "status": "active",
    },
    {
        "id": "patient_demo_002",
        "name": "李四",
        "gender": "女",
        "dob": date(1985, 8, 22),
        "phone": "13900004321",
        "allergies": [],
        "medical_history": ["哮喘"],
        "created_at": "2026-06-05T10:00:00+00:00",
        "last_visit": "2026-06-18T09:15:00+00:00",
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


def _authorize(record: dict | None, user_id: str) -> dict:
    """Enforce ownership: unowned (seeded) records are public, owned records
    require a matching user_id. Raises 404/403 otherwise."""
    if not record:
        raise HTTPException(status_code=404, detail="患者不存在")
    owner = record.get("owner_id")
    if owner and owner != user_id:
        raise HTTPException(status_code=403, detail="无权访问该患者")
    return record


def _row_to_dict(p: Patient) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "gender": p.gender,
        "dob": p.dob,
        "phone": p.phone,
        "allergies": list(p.allergies or []),
        "medical_history": list(p.medical_history or []),
        "created_at": p.created_at.isoformat() if p.created_at else "",
        "last_visit": p.last_visit.isoformat() if p.last_visit else None,
        "status": p.status or "active",
        "owner_id": p.owner_id,
    }


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
        owner_id=data.get("owner_id"),
    )


@router.get("", response_model=PatientListResponse)
async def list_patients(
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user),
):
    """List patients with optional search.

    Ownership: seeded demo patients (no owner) are visible to everyone;
    user-created patients (with owner_id) are visible only to their creator.
    """
    if db_enabled():
        async with AsyncSession() as session:
            rows, total = await patient_repo.list_patients(
                session,
                owner_id=user_id,
                search=search,
                offset=(page - 1) * page_size,
                limit=page_size,
            )
        return PatientListResponse(
            total=total, items=[_to_response(_row_to_dict(r)) for r in rows]
        )

    items = [
        p for p in _patients.values()
        if not p.get("owner_id") or p.get("owner_id") == user_id
    ]
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
    now = datetime.now(timezone.utc)

    if db_enabled():
        row = Patient(
            id=patient_id,
            owner_id=user_id,
            name=data.name,
            gender=data.gender,
            dob=data.dob,
            phone=data.phone,
            id_number=data.id_number,
            address=data.address,
            allergies=data.allergies or [],
            medical_history=data.medical_history or [],
            status="active",
            created_at=now,
        )
        async with AsyncSession() as session:
            row = await patient_repo.create_patient(session, row)
        logger.info("Created patient: %s (by user=%s)", patient_id, user_id)
        return _to_response(_row_to_dict(row))

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
        "created_at": now.isoformat(),
        "last_visit": None,
        "status": "active",
        "owner_id": user_id,
    }
    _patients[patient_id] = record
    logger.info("Created patient: %s (by user=%s)", patient_id, user_id)
    return _to_response(record)


@router.get("/me", response_model=PatientResponse, responses={404: {"description": "尚未创建个人档案"}})
async def get_my_profile(user_id: str = Depends(get_current_user)):
    """Return the patient profile owned by the current user.

    Declared before ``/{patient_id}`` so the literal path wins.

    Frontend pages previously hardcoded ``patient_demo_001``; this endpoint
    gives them a stable per-user profile instead. Returns 404 when the user
    has not created one yet, so the client can decide whether to provision it.
    """
    if db_enabled():
        async with AsyncSession() as session:
            row = await patient_repo.get_own_patient(session, owner_id=user_id)
        if row is None:
            raise HTTPException(status_code=404, detail="尚未创建个人档案")
        return _to_response(_row_to_dict(row))

    for record in _patients.values():
        if record.get("owner_id") == user_id:
            return _to_response(record)
    raise HTTPException(status_code=404, detail="尚未创建个人档案")


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    user_id: str = Depends(get_current_user),
):
    """Get patient details by ID."""
    if db_enabled():
        async with AsyncSession() as session:
            row = await patient_repo.get_patient(session, patient_id)
        record = _authorize(_row_to_dict(row) if row else None, user_id)
        return _to_response(record)

    record = _authorize(_patients.get(patient_id), user_id)
    return _to_response(record)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    user_id: str = Depends(get_current_user),
):
    """Update patient information."""
    update_data = data.model_dump(exclude_unset=True)

    if db_enabled():
        async with AsyncSession() as session:
            row = await patient_repo.get_patient(session, patient_id)
            _authorize(_row_to_dict(row) if row else None, user_id)
            for key, value in update_data.items():
                setattr(row, key, value)
            await session.commit()
            await session.refresh(row)
            result = _row_to_dict(row)
        logger.info("Updated patient: %s (by user=%s)", patient_id, user_id)
        return _to_response(result)

    record = _authorize(_patients.get(patient_id), user_id)
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
    if db_enabled():
        async with AsyncSession() as session:
            row = await patient_repo.get_patient(session, patient_id)
            _authorize(_row_to_dict(row) if row else None, user_id)
            await patient_repo.delete_patient(session, row)
        logger.info("Deleted patient: %s (by user=%s)", patient_id, user_id)
        return {"message": f"患者 {patient_id} 已删除"}

    _authorize(_patients.get(patient_id), user_id)
    del _patients[patient_id]
    logger.info("Deleted patient: %s (by user=%s)", patient_id, user_id)
    return {"message": f"患者 {patient_id} 已删除"}
