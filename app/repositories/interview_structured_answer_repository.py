from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_structured_answer import InterviewStructuredAnswer


class InterviewStructuredAnswerRepository:
    def create(
        self,
        db: Session,
        answer: InterviewStructuredAnswer,
    ) -> InterviewStructuredAnswer:
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    def get_by_session_and_question_id(
        self,
        db: Session,
        session_id: str,
        question_id: str,
    ) -> InterviewStructuredAnswer | None:
        stmt = select(InterviewStructuredAnswer).where(
            InterviewStructuredAnswer.session_id == session_id,
            InterviewStructuredAnswer.question_id == question_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_by_session_id(
        self,
        db: Session,
        session_id: str,
    ) -> list[InterviewStructuredAnswer]:
        stmt = (
            select(InterviewStructuredAnswer)
            .where(InterviewStructuredAnswer.session_id == session_id)
            .order_by(InterviewStructuredAnswer.created_at.asc())
        )
        return list(db.execute(stmt).scalars().all())