from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.clients.campaign_service_client import campaign_service_client
from app.clients.invitation_service_client import invitation_service_client
from app.models.interview_message import InterviewMessage
from app.models.interview_report import InterviewReport
from app.models.interview_session import InterviewSession
from app.models.interview_structured_answer import InterviewStructuredAnswer
from app.repositories.interview_message_repository import InterviewMessageRepository
from app.repositories.interview_report_repository import InterviewReportRepository
from app.repositories.interview_session_repository import InterviewSessionRepository
from app.repositories.interview_structured_answer_repository import (
    InterviewStructuredAnswerRepository,
)
from app.services.report_service import report_service


class InterviewService:
    def __init__(self) -> None:
        self._session_repository = InterviewSessionRepository()
        self._message_repository = InterviewMessageRepository()
        self._report_repository = InterviewReportRepository()
        self._structured_answer_repository = InterviewStructuredAnswerRepository()

    def start_session(
        self,
        db: Session,
        invite_token: str,
    ) -> dict:
        invitation = invitation_service_client.get_invitation_by_token(invite_token)
        campaign = campaign_service_client.get_interview_config(
            campaign_id=invitation["campaignId"],
            tenant_id=invitation["tenantId"],
        )

        existing = self._session_repository.get_active_by_invitation_id(
            db=db,
            invitation_id=invitation["invitationId"],
        )
        if existing is not None:
            return self._to_session_response(existing, campaign)

        questions = campaign["questions"]
        first_question = questions[0]
        now = datetime.now(UTC).replace(tzinfo=None)

        session_obj = InterviewSession(
            session_id=f"sess_{uuid4().hex[:12]}",
            tenant_id=invitation["tenantId"],
            campaign_id=invitation["campaignId"],
            invitation_id=invitation["invitationId"],
            invite_token=invite_token,
            status="in_progress",
            current_question_index=0,
            current_question_id=first_question["id"],
            follow_up_count_for_current_question=0,
            started_at=now,
            completed_at=None,
            created_at=now,
            updated_at=now,
        )

        created_session = self._session_repository.create(db, session_obj)

        assistant_message = InterviewMessage(
            message_id=f"msg_{uuid4().hex[:12]}",
            session_id=created_session.session_id,
            role="assistant",
            content=first_question["text"],
            question_id=first_question["id"],
            created_at=now,
        )
        self._message_repository.create(db, assistant_message)

        return self._to_session_response(created_session, campaign)

    def get_session(
        self,
        db: Session,
        session_id: str,
    ) -> dict:
        session_obj = self._session_repository.get_by_id(db, session_id)
        if session_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )

        campaign = campaign_service_client.get_interview_config(
            campaign_id=session_obj.campaign_id,
            tenant_id=session_obj.tenant_id,
        )
        return self._to_session_response(session_obj, campaign)

    def process_message(
        self,
        db: Session,
        session_id: str,
        message: str,
    ) -> dict:
        session_obj = self._session_repository.get_by_id(db, session_id)
        if session_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )

        if session_obj.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Interview session is already completed",
            )

        campaign = campaign_service_client.get_interview_config(
            campaign_id=session_obj.campaign_id,
            tenant_id=session_obj.tenant_id,
        )
        questions = campaign["questions"]

        if session_obj.current_question_index >= len(questions):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Interview session is ready to finalize",
            )

        current_question = questions[session_obj.current_question_index]
        now = datetime.now(UTC).replace(tzinfo=None)
        user_text = message.strip()

        user_message = InterviewMessage(
            message_id=f"msg_{uuid4().hex[:12]}",
            session_id=session_obj.session_id,
            role="user",
            content=user_text,
            question_id=current_question["id"],
            created_at=now,
        )
        self._message_repository.create(db, user_message)

        existing_structured = self._structured_answer_repository.get_by_session_and_question_id(
            db=db,
            session_id=session_obj.session_id,
            question_id=current_question["id"],
        )

        if existing_structured is None:
            structured_answer = InterviewStructuredAnswer(
                structured_answer_id=f"ans_{uuid4().hex[:12]}",
                session_id=session_obj.session_id,
                question_id=current_question["id"],
                question_text=current_question["text"],
                question_objective=current_question["objective"],
                answer_text=user_text,
                follow_ups_json=[],
                created_at=now,
                updated_at=now,
            )
            self._structured_answer_repository.create(db, structured_answer)
        else:
            follow_ups = list(existing_structured.follow_ups_json or [])
            follow_ups.append(
                {
                    "answer": user_text,
                    "recordedAt": now.isoformat(),
                }
            )
            existing_structured.answer_text = user_text
            existing_structured.follow_ups_json = follow_ups
            existing_structured.updated_at = now
            db.add(existing_structured)
            db.commit()
            db.refresh(existing_structured)

        next_index = session_obj.current_question_index + 1

        if next_index >= len(questions):
            session_obj.current_question_index = len(questions)
            session_obj.current_question_id = None
            session_obj.follow_up_count_for_current_question = 0
            session_obj.updated_at = now
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)

            assistant_text = "Gracias. La entrevista quedó lista para finalizar."
            session_completed = True
            assistant_question_id = None
        else:
            next_question = questions[next_index]
            session_obj.current_question_index = next_index
            session_obj.current_question_id = next_question["id"]
            session_obj.follow_up_count_for_current_question = 0
            session_obj.updated_at = now
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)

            assistant_text = next_question["text"]
            session_completed = False
            assistant_question_id = next_question["id"]

        assistant_message = InterviewMessage(
            message_id=f"msg_{uuid4().hex[:12]}",
            session_id=session_obj.session_id,
            role="assistant",
            content=assistant_text,
            question_id=assistant_question_id,
            created_at=now,
        )
        self._message_repository.create(db, assistant_message)

        return {
            "assistantMessage": assistant_text,
            "sessionCompleted": session_completed,
        }

    def finalize_session(
        self,
        db: Session,
        session_id: str,
        include_transcript: bool,
    ) -> dict:
        session_obj = self._session_repository.get_by_id(db, session_id)
        if session_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )

        existing_report = self._report_repository.get_by_session_id(db, session_id)
        if existing_report is not None:
            invitation_service_client.mark_invitation_completed(session_obj.invitation_id)
            return {"report": existing_report.report_json}

        campaign = campaign_service_client.get_interview_config(
            campaign_id=session_obj.campaign_id,
            tenant_id=session_obj.tenant_id,
        )
        questions = campaign["questions"]

        if session_obj.current_question_index < len(questions):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Interview session is not ready to finalize",
            )

        messages = self._message_repository.list_by_session_id(db, session_id)
        structured_answers = self._structured_answer_repository.list_by_session_id(
            db=db,
            session_id=session_id,
        )

        report = report_service.build_report(
            session_obj=session_obj,
            campaign=campaign,
            messages=messages,
            structured_answers=structured_answers,
            include_transcript=include_transcript,
        )

        now = datetime.now(UTC).replace(tzinfo=None)

        session_obj.status = "completed"
        session_obj.completed_at = now
        session_obj.updated_at = now
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

        report_obj = InterviewReport(
            report_id=f"rep_{uuid4().hex[:12]}",
            session_id=session_obj.session_id,
            tenant_id=session_obj.tenant_id,
            campaign_id=session_obj.campaign_id,
            report_json=report,
            created_at=now,
        )
        self._report_repository.create(db, report_obj)

        invitation_service_client.mark_invitation_completed(session_obj.invitation_id)

        return {"report": report}

    @staticmethod
    def _to_session_response(
        session_obj: InterviewSession,
        campaign: dict,
    ) -> dict:
        questions = campaign["questions"]
        current_index = session_obj.current_question_index

        if current_index >= len(questions):
            assistant_message = "La entrevista quedó lista para finalizar."
            session_completed = True
        else:
            assistant_message = questions[current_index]["text"]
            session_completed = False

        return {
            "sessionId": session_obj.session_id,
            "campaignId": session_obj.campaign_id,
            "campaignName": campaign["campaignName"],
            "assistantMessage": assistant_message,
            "sessionCompleted": session_completed,
        }


interview_service = InterviewService()