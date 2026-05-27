"""Identity verification guard — pre-hook for every patient data access."""


class IdentityVerifier:
    async def verify(self, patient_id: str, session_patient_id: str) -> bool:
        return patient_id == session_patient_id
