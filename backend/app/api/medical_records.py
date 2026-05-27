from fastapi import APIRouter

router = APIRouter()


@router.get("/{record_id}")
async def get_medical_record(record_id: str):
    return {"record_id": record_id}
