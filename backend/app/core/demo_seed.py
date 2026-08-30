"""Idempotent demo seeding for DEMO_MODE when a database is available.

Seeds two demo accounts (patient + doctor) and the demo patient/record data
so the online demo stays explorable while all authentication is real.
"""

import logging
from datetime import date, datetime

from app.core.password import hash_password
from app.models import MedicalRecord, Patient, User

logger = logging.getLogger(__name__)

DEMO_PASSWORD = "Demo@12345"

_DEMO_USERS = [
    ("user_demo_patient", "demo@medinexus.dev", "张三", "patient"),
    ("user_demo_doctor", "doctor@medinexus.dev", "李医生", "doctor"),
]

_DEMO_PATIENTS = [
    {
        "id": "patient_demo_001",
        "name": "张三",
        "gender": "男",
        "dob": date(1990, 5, 15),
        "phone": "13800005678",
        "allergies": ["青霉素"],
        "medical_history": ["高血压"],
        "created_at": datetime.fromisoformat("2026-06-01T08:00:00+00:00"),
        "last_visit": datetime.fromisoformat("2026-06-20T14:30:00+00:00"),
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
        "created_at": datetime.fromisoformat("2026-06-05T10:00:00+00:00"),
        "last_visit": datetime.fromisoformat("2026-06-18T09:15:00+00:00"),
        "status": "active",
    },
]

_DEMO_RECORDS = [
    {
        "id": "record_001",
        "patient_id": "patient_demo_001",
        "date": datetime.fromisoformat("2026-06-20T14:30:00+00:00"),
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
        "date": datetime.fromisoformat("2026-06-10T09:00:00+00:00"),
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
        "date": datetime.fromisoformat("2026-06-18T09:15:00+00:00"),
        "subjective": "喘息发作2天，接触花粉后",
        "objective": "双肺散在哮鸣音，呼吸频率22次/分",
        "assessment": "支气管哮喘急性发作",
        "plan": "沙丁胺醇气雾剂2吸 prn，布地奈德福莫特罗1吸 bid",
        "diagnosis": "哮喘",
        "department": "呼吸科",
        "doctor": "AI辅助诊断",
    },
]


async def seed_demo_data() -> None:
    """Insert demo users/patients/records if they don't already exist."""
    from app.core.database import AsyncSession

    async with AsyncSession() as session:
        for user_id, email, name, role in _DEMO_USERS:
            if await session.get(User, user_id) is None:
                session.add(
                    User(
                        id=user_id,
                        email=email,
                        password_hash=hash_password(DEMO_PASSWORD),
                        name=name,
                        role=role,
                    )
                )
                logger.info("Seeded demo user: %s (%s)", email, DEMO_PASSWORD)

        for data in _DEMO_PATIENTS:
            if await session.get(Patient, data["id"]) is None:
                session.add(Patient(**data))

        for data in _DEMO_RECORDS:
            if await session.get(MedicalRecord, data["id"]) is None:
                session.add(MedicalRecord(**data))

        await session.commit()
