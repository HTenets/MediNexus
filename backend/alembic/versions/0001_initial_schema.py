"""Initial schema — users, patients, consultations, records, and supporting tables.

Revision ID: 0001
Revises:
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="patient"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "patients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("id_number", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("allergies", sa.JSON(), nullable=True),
        sa.Column("medical_history", sa.JSON(), nullable=True),
        sa.Column("last_visit", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=True, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_patients_owner_id", "patients", ["owner_id"])

    op.create_table(
        "consultations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(), nullable=True, server_default="active"),
        sa.Column("current_agent", sa.String(), nullable=True, server_default="triage"),
        sa.Column("history", sa.JSON(), nullable=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_consultations_patient_id", "consultations", ["patient_id"])
    op.create_index("ix_consultations_owner_id", "consultations", ["owner_id"])

    op.create_table(
        "medical_records",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_id", sa.String(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subjective", sa.Text(), nullable=True),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("assessment", sa.Text(), nullable=True),
        sa.Column("plan", sa.Text(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("doctor", sa.String(), nullable=True),
    )
    op.create_index("ix_medical_records_patient_id", "medical_records", ["patient_id"])

    op.create_table(
        "prescriptions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("consultation_id", sa.String(), sa.ForeignKey("consultations.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("review_status", sa.String(), nullable=True, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "medical_histories",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_id", sa.String(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("history_type", sa.String(), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "followups",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_id", sa.String(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("consultation_id", sa.String(), sa.ForeignKey("consultations.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=True, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("followups")
    op.drop_table("medical_histories")
    op.drop_table("prescriptions")
    op.drop_index("ix_medical_records_patient_id", table_name="medical_records")
    op.drop_table("medical_records")
    op.drop_index("ix_consultations_owner_id", table_name="consultations")
    op.drop_index("ix_consultations_patient_id", table_name="consultations")
    op.drop_table("consultations")
    op.drop_index("ix_patients_owner_id", table_name="patients")
    op.drop_table("patients")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
