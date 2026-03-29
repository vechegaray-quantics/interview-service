"""create interview reports table

Revision ID: 72b92d9fa6d4
Revises: 1b8f2a4d9c01
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "72b92d9fa6d4"
down_revision: Union[str, None] = "1b8f2a4d9c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_reports",
        sa.Column("report_id", sa.String(length=40), nullable=False),
        sa.Column("session_id", sa.String(length=40), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("campaign_id", sa.String(length=32), nullable=False),
        sa.Column("report_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("report_id"),
    )
    op.create_index("ix_interview_reports_session_id", "interview_reports", ["session_id"], unique=True)
    op.create_index("ix_interview_reports_tenant_id", "interview_reports", ["tenant_id"])
    op.create_index("ix_interview_reports_campaign_id", "interview_reports", ["campaign_id"])


def downgrade() -> None:
    op.drop_index("ix_interview_reports_campaign_id", table_name="interview_reports")
    op.drop_index("ix_interview_reports_tenant_id", table_name="interview_reports")
    op.drop_index("ix_interview_reports_session_id", table_name="interview_reports")
    op.drop_table("interview_reports")