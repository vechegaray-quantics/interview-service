from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.interview import InterviewSessionResponse, StartInterviewRequest
from app.schemas.message import InterviewMessageRequest, InterviewTurnResponse
from app.schemas.report import FinalizeInterviewRequest, FinalizeInterviewResponse
from app.services.interview_service import interview_service


router = APIRouter(prefix="/public/v1/interviews", tags=["public-interviews"])


@router.post("/start", response_model=InterviewSessionResponse)
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    result = interview_service.start_session(
        db=db,
        invite_token=payload.inviteToken,
    )
    return InterviewSessionResponse(**result)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    result = interview_service.get_session(
        db=db,
        session_id=session_id,
    )
    return InterviewSessionResponse(**result)


@router.post("/{session_id}/messages", response_model=InterviewTurnResponse)
def post_interview_message(
    session_id: str,
    payload: InterviewMessageRequest,
    db: Session = Depends(get_db),
) -> InterviewTurnResponse:
    result = interview_service.process_message(
        db=db,
        session_id=session_id,
        message=payload.message,
    )
    return InterviewTurnResponse(**result)


@router.post("/{session_id}/finalize", response_model=FinalizeInterviewResponse)
def finalize_interview_session(
    session_id: str,
    payload: FinalizeInterviewRequest,
    db: Session = Depends(get_db),
) -> FinalizeInterviewResponse:
    result = interview_service.finalize_session(
        db=db,
        session_id=session_id,
        include_transcript=payload.includeTranscript,
    )
    return FinalizeInterviewResponse(**result)