"""Medical records API — CRUD for consultation records."""
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.consultation import ConsultationHistoryResponse
from app.core.auth import get_current_user
from app.api.patients import _patients as _patient_store

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store (PostgreSQL in production)
_records: dict[str, list[dict]] = {}


def _authorize_patient(patient_id: str, user_id: str) -> None:
    """Reject access to records of a patient owned by another user.

    Unowned patients (seeded demo data) are public. Owned patients require
    a matching user_id, mirroring the ownership rule in patients.py.
    """
    patient = _patient_store.get(patient_id)
    if patient and patient.get("owner_id") and patient.get("owner_id") != user_id:
        raise HTTPException(status_code=403, detail="无权访问该患者")

# Seed demo records
_demo_records = [
    {
        "id": "record_001",
        "patient_id": "patient_demo_001",
        "date": "2026-06-20T14:30:00",
        "subjective": "头痛两天，伴低热37.8°C",
        "objective": "体温37.8°C，咽部充血，扁桃体I度肿大",
        "assessment": "急性上呼吸道感染",
        "plan": "对乙酰氨基酚500mg po prn，多饮水休息",
        "diagnosis": "感冒",
        "department": "内科",
        "doctor": "AI辅助诊断",
    },
    {
        "id": "record_002",
        "patient_id": "patient_demo_001",
        "date": "2026-06-10T09:00:00",
        "subjective": "血压偏高复查",
        "objective": "BP 145/92mmHg",
        "assessment": "高血压1级",
        "plan": "继续服用氨氯地平5mg qd，低盐饮食",
        "diagnosis": "高血压",
        "department": "心内科",
        "doctor": "AI辅助诊断",
    },
    {
        "id": "record_003",
        "patient_id": "patient_demo_002",
        "date": "2026-06-18T09:15:00",
        "subjective": "喘息发作2天，接触花粉后",
        "objective": "双肺散在哮鸣音，呼吸频率22次/分",
        "assessment": "支气管哮喘急性发作",
        "plan": "沙丁胺醇气雾剂2吸 prn，布地奈德福莫特罗1吸 bid",
        "diagnosis": "哮喘",
        "department": "呼吸科",
        "doctor": "AI辅助诊断",
    },
]
for r in _demo_records:
    pid = r["patient_id"]
    if pid not in _records:
        _records[pid] = []
    _records[pid].append(r)


@router.get("/{record_id}")
async def get_medical_record(record_id: str, user_id: str = Depends(get_current_user)):
    """Get a single medical record by ID."""
    for pid, items in _records.items():
        for r in items:
            if r["id"] == record_id:
                _authorize_patient(pid, user_id)
                return r
    raise HTTPException(status_code=404, detail=f"病历 {record_id} 不存在")


@router.get("/patient/{patient_id}", response_model=ConsultationHistoryResponse)
async def list_patient_records(patient_id: str, user_id: str = Depends(get_current_user)):
    """List all records for a patient."""
    _authorize_patient(patient_id, user_id)
    items = _records.get(patient_id, [])
    items_sorted = sorted(items, key=lambda x: x.get("date", ""), reverse=True)
    return ConsultationHistoryResponse(
        session_id=patient_id,
        records=items_sorted,
        total=len(items_sorted),
    )


@router.post("/patient/{patient_id}", status_code=201)
async def create_medical_record(
    patient_id: str,
    data: dict,
    user_id: str = Depends(get_current_user),
):
    """Create a new medical record for a patient."""
    _authorize_patient(patient_id, user_id)
    record_id = f"record_{uuid.uuid4().hex[:8]}"
    record = {
        "id": record_id,
        "patient_id": patient_id,
        "date": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    if patient_id not in _records:
        _records[patient_id] = []
    _records[patient_id].append(record)
    logger.info("Created record %s for patient %s", record_id, patient_id)
    return record
