"""Identity verification guard — pre-hook for every patient data access."""

import logging

logger = logging.getLogger(__name__)


class IdentityVerifier:
    """Verifies patient identity for data access requests."""

    async def verify(self, patient_id: str, session_patient_id: str) -> tuple[bool, str]:
        """Verify that the requested patient_id matches the session's patient_id.

        Returns (is_verified, reason)."""
        if patient_id == session_patient_id:
            return True, "ok"
        return False, f"identity_mismatch: {patient_id} != {session_patient_id}"

    async def verify_session(self, session_id: str, patient_id: str) -> bool:
        """Verify that a session belongs to the given patient.

        Demo mode: always returns True.
        """
        logger.debug("Session verification: session=%s, patient=%s (demo mode: always ok)", session_id, patient_id)
        return True
