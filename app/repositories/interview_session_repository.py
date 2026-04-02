from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_session import InterviewSession


class InterviewSessionRepository:
    def create(
        self,
        db: Session,
        session_obj: InterviewSession,
    ) -> InterviewSession:
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        return session_obj

    def get_by_id(
        self,
        db: Session,
        session_id: str,
    ) -> InterviewSession | None:
        stmt = select(InterviewSession).where(InterviewSession.session_id == session_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_active_by_invitation_id(
        self,
        db: Session,
        invitation_id: str,
    ) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(
                InterviewSession.invitation_id == invitation_id,
                InterviewSession.status == "in_progress",
            )
            .order_by(InterviewSession.created_at.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_latest_by_invitation_id(
        self,
        db: Session,
        invitation_id: str,
    ) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.invitation_id == invitation_id)
            .order_by(InterviewSession.created_at.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()