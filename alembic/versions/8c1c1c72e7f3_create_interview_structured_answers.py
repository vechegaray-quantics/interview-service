"""create interview structured answers

Revision ID: 8c1c1c72e7f3
Revises: 72b92d9fa6d4
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c1c1c72e7f3"
down_revision: Union[str, None] = "72b92d9fa6d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_structured_answers",
        sa.Column("structured_answer_id", sa.String(length=40), nullable=False),
        sa.Column("session_id", sa.String(length=40), nullable=False),
        sa.Column("question_id", sa.String(length=64), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_objective", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("follow_ups_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("structured_answer_id"),
        sa.UniqueConstraint(
            "session_id",
            "question_id",
            name="uq_interview_structured_answers_session_question",
        ),
    )
    op.create_index(
        "ix_interview_structured_answers_session_id",
        "interview_structured_answers",
        ["session_id"],
    )
    op.create_index(
        "ix_interview_structured_answers_question_id",
        "interview_structured_answers",
        ["question_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_interview_structured_answers_question_id",
        table_name="interview_structured_answers",
    )
    op.drop_index(
        "ix_interview_structured_answers_session_id",
        table_name="interview_structured_answers",
    )
    op.drop_table("interview_structured_answers")