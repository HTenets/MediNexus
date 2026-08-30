"""Patient persistence."""

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MedicalRecord, Patient


def _visibility_filter(owner_id: str):
    return or_(Patient.owner_id.is_(None), Patient.owner_id == owner_id)


async def list_patients(
    session: AsyncSession,
    *,
    owner_id: str,
    search: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Patient], int]:
    base = select(Patient).where(_visibility_filter(owner_id))
    if search:
        base = base.where(Patient.name.ilike(f"%{search}%"))

    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = await session.execute(
        base.order_by(Patient.created_at.desc().nulls_last(), Patient.id).offset(offset).limit(limit)
    )
    return list(rows.scalars().all()), total


async def get_patient(session: AsyncSession, patient_id: str) -> Patient | None:
    return await session.get(Patient, patient_id)


async def get_own_patient(session: AsyncSession, *, owner_id: str) -> Patient | None:
    """The patient profile owned by this user (their own record), if any."""
    rows = await session.execute(
        select(Patient)
        .where(Patient.owner_id == owner_id)
        .order_by(Patient.created_at.asc())
        .limit(1)
    )
    return rows.scalars().first()


async def create_patient(session: AsyncSession, patient: Patient) -> Patient:
    session.add(patient)
    await session.commit()
    await session.refresh(patient)
    return patient


async def delete_patient(session: AsyncSession, patient: Patient) -> None:
    # Cascade: remove dependent visit records (FK to patients)
    await session.execute(
        delete(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
    )
    await session.delete(patient)
    await session.commit()
