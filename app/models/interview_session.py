from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    session_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    campaign_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    invitation_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    invite_token: Mapped[str] = mapped_column(String(80), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_question_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_question_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    follow_up_count_for_current_question: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)