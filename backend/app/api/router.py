from fastapi import APIRouter
from . import consultation, patients, medical_records, health, auth, knowledge

api_router = APIRouter()
api_router.include_router(consultation.router, prefix="/consult", tags=["consultation"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(medical_records.router, prefix="/records", tags=["records"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(health.router, prefix="", tags=["health"])
