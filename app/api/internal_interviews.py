from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.db import get_db
from app.services.interview_service import interview_service


router = APIRouter(prefix="/internal/v1/interviews", tags=["internal-interviews"])


def _validate_internal_token(x_internal_service_token: str) -> None:
    if not x_internal_service_token or not compare_digest(
        x_internal_service_token,
        settings.internal_service_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token",
        )


@router.get("/by-invitation/{invitation_id}")
def get_interview_by_invitation(
    invitation_id: str,
    db: Session = Depends(get_db),
    x_internal_service_token: str = Header(default="", alias="X-Internal-Service-Token"),
) -> dict:
    _validate_internal_token(x_internal_service_token)
    return interview_service.get_internal_session_by_invitation(db, invitation_id)