from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    report_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    campaign_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)