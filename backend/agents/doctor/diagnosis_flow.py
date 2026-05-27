"""Diagnosis flow state machine."""

class DiagnosisState:
    INITIAL = "initial"
    HISTORY_TAKING = "history_taking"
    DIFFERENTIAL = "differential"
    TREATMENT = "treatment"
    COMPLETED = "completed"
