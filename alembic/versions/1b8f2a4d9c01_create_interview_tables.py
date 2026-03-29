"""create interview tables

Revision ID: 1b8f2a4d9c01
Revises:
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1b8f2a4d9c01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("session_id", sa.String(length=40), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("campaign_id", sa.String(length=32), nullable=False),
        sa.Column("invitation_id", sa.String(length=40), nullable=False),
        sa.Column("invite_token", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_question_index", sa.Integer(), nullable=False),
        sa.Column("current_question_id", sa.String(length=64), nullable=True),
        sa.Column("follow_up_count_for_current_question", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_index("ix_interview_sessions_tenant_id", "interview_sessions", ["tenant_id"])
    op.create_index("ix_interview_sessions_campaign_id", "interview_sessions", ["campaign_id"])
    op.create_index("ix_interview_sessions_invitation_id", "interview_sessions", ["invitation_id"])
    op.create_index("ix_interview_sessions_invite_token", "interview_sessions", ["invite_token"])

    op.create_table(
        "interview_messages",
        sa.Column("message_id", sa.String(length=40), nullable=False),
        sa.Column("session_id", sa.String(length=40), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("question_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index("ix_interview_messages_session_id", "interview_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_interview_messages_session_id", table_name="interview_messages")
    op.drop_table("interview_messages")

    op.drop_index("ix_interview_sessions_invite_token", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_invitation_id", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_campaign_id", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_tenant_id", table_name="interview_sessions")
    op.drop_table("interview_sessions")