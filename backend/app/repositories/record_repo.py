"""Medical record persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MedicalRecord


async def list_by_patient(session: AsyncSession, patient_id: str) -> list[MedicalRecord]:
    rows = await session.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.date.desc().nulls_last())
    )
    return list(rows.scalars().all())


async def get_record(session: AsyncSession, record_id: str) -> MedicalRecord | None:
    return await session.get(MedicalRecord, record_id)


async def create_record(session: AsyncSession, record: MedicalRecord) -> MedicalRecord:
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record
