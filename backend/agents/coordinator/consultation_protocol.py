"""Consultation protocol — state machine and data structures."""


class ConsultationState:
    PENDING = "pending"
    SPECIALISTS_INVITED = "specialists_invited"
    OPINIONS_COLLECTED = "opinions_collected"
    CONSENSUS_REACHED = "consensus_reached"
    COMPLETED = "completed"
