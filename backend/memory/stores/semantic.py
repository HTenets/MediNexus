"""Semantic memory (tier 3) — durable patient profile.

Holds the facts that should persist across visits: demographics, allergies,
chronic conditions, and long-term medication history.

Primary store is the ``patients`` table. Without a database the facts are kept
in a module-level in-process store so a demo deployment still accumulates a
profile within a process (and ``add_history`` is not a silent no-op).
"""

import logging
from typing import Any

from app.core.database import AsyncSession, db_enabled

logger = logging.getLogger(__name__)

#: Process-local fallback for deployments without a database.
_FALLBACK: dict[str, dict] = {}

_HISTORY_KINDS = ("allergy", "condition", "medication", "note")


def _empty_profile() -> dict:
    return {"patient_info": {}, "allergies": [], "medical_history": []}


class SemanticMemory:
    """Long-term patient profile: allergies, conditions, demographics."""

    # ── Read ──────────────────────────────────────────────────────────── #

    async def get_profile(self, patient_id: str) -> dict:
        """Return ``{"patient_info": {...}, "allergies": [...], "medical_history": [...]}``."""
        if not patient_id:
            return _empty_profile()

        if db_enabled():
            profile = await self._profile_from_db(patient_id)
            if profile is not None:
                return profile

        return self._profile_from_fallback(patient_id)

    async def get_allergies(self, patient_id: str) -> list:
        profile = await self.get_profile(patient_id)
        return list(profile.get("allergies") or [])

    async def format_profile(self, patient_id: str) -> str:
        """Render the profile as a compact block for LLM context injection.

        Returns an empty string when nothing is known, so callers can skip the
        section entirely rather than injecting noise.
        """
        profile = await self.get_profile(patient_id)
        info = profile.get("patient_info") or {}
        allergies = profile.get("allergies") or []
        history = profile.get("medical_history") or []

        lines: list[str] = []
        bits = [
            f"{info['gender']}" if info.get("gender") else "",
            f"{info['age']}岁" if info.get("age") else "",
        ]
        demographics = "，".join(b for b in bits if b)
        if demographics or info.get("name"):
            lines.append(f"- 患者: {info.get('name') or '未知'}{('（' + demographics + '）') if demographics else ''}")
        if allergies:
            lines.append(f"- 过敏史: {('、'.join(str(a) for a in allergies))}")
        if history:
            lines.append(f"- 既往病史: {('、'.join(str(h) for h in history))}")

        return "\n".join(lines)

    # ── Write ─────────────────────────────────────────────────────────── #

    async def add_history(self, patient_id: str, kind: str, data: Any) -> bool:
        """Append a fact to the patient's profile.

        ``kind`` is one of ``allergy`` / ``condition`` / ``medication`` / ``note``.
        Returns True when the fact was stored.
        """
        if not patient_id or kind not in _HISTORY_KINDS:
            return False

        if db_enabled() and await self._add_history_db(patient_id, kind, data):
            return True
        if db_enabled():
            # DB configured but the patient row is missing (ad-hoc session
            # patient id) — fall through so the fact isn't silently dropped.
            logger.debug("Semantic memory: no patient row for %s, using fallback", patient_id)

        return self._add_history_fallback(patient_id, kind, data)

    # ── Database layer ────────────────────────────────────────────────── #

    async def _profile_from_db(self, patient_id: str) -> dict | None:
        from sqlalchemy import select
        from app.models import Patient

        try:
            async with AsyncSession() as session:
                row = (
                    await session.execute(select(Patient).where(Patient.id == patient_id))
                ).scalar_one_or_none()
        except Exception as e:  # noqa: BLE001 - memory must never break the pipeline
            logger.warning("Semantic memory DB read failed for %s: %s", patient_id, e)
            return None

        if row is None:
            return None

        from datetime import date

        age = None
        if row.dob:
            today = date.today()
            dob = row.dob if isinstance(row.dob, date) else row.dob
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        return {
            "patient_info": {
                "name": row.name,
                "gender": row.gender,
                "age": age,
                "phone": row.phone,
            },
            "allergies": list(row.allergies or []),
            "medical_history": list(row.medical_history or []),
        }

    async def _add_history_db(self, patient_id: str, kind: str, data: Any) -> bool:
        from sqlalchemy import select
        from app.models import Patient

        try:
            async with AsyncSession() as session:
                row = (
                    await session.execute(select(Patient).where(Patient.id == patient_id))
                ).scalar_one_or_none()
                if row is None:
                    return False

                if kind == "allergy":
                    target = list(row.allergies or [])
                else:
                    target = list(row.medical_history or [])

                entry = data if isinstance(data, str) else (data or {}).get("name", str(data))
                # Re-assign: SQLAlchemy JSON columns don't track in-place mutation
                if entry and entry not in target:
                    target = target + [entry]
                if kind == "allergy":
                    row.allergies = target
                else:
                    row.medical_history = target
                await session.commit()
                return True
        except Exception as e:  # noqa: BLE001
            logger.warning("Semantic memory DB write failed for %s: %s", patient_id, e)
            return False

    # ── In-process fallback ───────────────────────────────────────────── #

    def _profile_from_fallback(self, patient_id: str) -> dict:
        stored = _FALLBACK.get(patient_id)
        if not stored:
            return _empty_profile()
        return {
            "patient_info": dict(stored.get("patient_info") or {}),
            "allergies": list(stored.get("allergies") or []),
            "medical_history": list(stored.get("medical_history") or []),
        }

    def _add_history_fallback(self, patient_id: str, kind: str, data: Any) -> bool:
        entry = data if isinstance(data, str) else (data or {}).get("name", str(data))
        if not entry:
            return False

        profile = _FALLBACK.setdefault(patient_id, _empty_profile())
        bucket = "allergies" if kind == "allergy" else "medical_history"
        if entry in profile[bucket]:
            return True
        profile[bucket].append(entry)
        return True
