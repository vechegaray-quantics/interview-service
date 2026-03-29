from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_report import InterviewReport


class InterviewReportRepository:
    def create(
        self,
        db: Session,
        report: InterviewReport,
    ) -> InterviewReport:
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def get_by_session_id(
        self,
        db: Session,
        session_id: str,
    ) -> InterviewReport | None:
        stmt = select(InterviewReport).where(InterviewReport.session_id == session_id)
        return db.execute(stmt).scalar_one_or_none()