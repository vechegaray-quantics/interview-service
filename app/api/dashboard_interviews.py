from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.services.interview_service import interview_service


router = APIRouter(prefix="/v1/interviews", tags=["dashboard-interviews"])


def get_tenant_id(
    x_tenant_id: str = Header(default="", alias="X-Tenant-Id"),
) -> str:
    tenant_id = x_tenant_id.strip()
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required",
        )
    return tenant_id


@router.get("/by-invitation/{invitation_id}")
def get_interview_by_invitation(
    invitation_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return interview_service.get_dashboard_session_by_invitation(
        db=db,
        invitation_id=invitation_id,
        tenant_id=tenant_id,
    )