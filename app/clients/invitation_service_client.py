import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class InvitationServiceClient:
    def get_invitation_by_token(self, invite_token: str) -> dict:
        base_url = settings.invitation_service_base_url.rstrip("/")
        url = f"{base_url}/internal/v1/invitations/by-token/{invite_token}"

        try:
            response = httpx.get(
                url,
                headers={
                    "X-Internal-Service-Token": settings.internal_service_token,
                },
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Invitation service unavailable: {exc}",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        if response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invitation service rejected internal authentication",
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invitation service returned an unexpected error",
            )

        return response.json()
        

invitation_service_client = InvitationServiceClient()