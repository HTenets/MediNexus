from fastapi import APIRouter

router = APIRouter()


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    return {"patient_id": patient_id}
