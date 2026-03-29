from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_message import InterviewMessage


class InterviewMessageRepository:
    def create(
        self,
        db: Session,
        message: InterviewMessage,
    ) -> InterviewMessage:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def list_by_session_id(
        self,
        db: Session,
        session_id: str,
    ) -> list[InterviewMessage]:
        stmt = (
            select(InterviewMessage)
            .where(InterviewMessage.session_id == session_id)
            .order_by(InterviewMessage.created_at.asc())
        )
        return list(db.execute(stmt).scalars().all())