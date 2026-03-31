import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class InvitationServiceClient:
    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "X-Internal-Service-Token": settings.internal_service_token,
        }

    def get_invitation_by_token(self, invite_token: str) -> dict:
        base_url = settings.invitation_service_base_url.rstrip("/")
        url = f"{base_url}/internal/v1/invitations/by-token/{invite_token}"

        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Invitation service unavailable at {base_url}: {exc}",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        if response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation service rejected internal authentication. "
                    "Check INTERNAL_SERVICE_TOKEN and INVITATION_SERVICE_BASE_URL."
                ),
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation service returned an unexpected error while "
                    "resolving the invitation token."
                ),
            )

        return response.json()

    def mark_invitation_completed(self, invitation_id: str) -> None:
        base_url = settings.invitation_service_base_url.rstrip("/")
        url = f"{base_url}/internal/v1/invitations/{invitation_id}/complete"

        try:
            response = httpx.post(
                url,
                headers=self._headers(),
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Invitation completion sync failed against {base_url}: {exc}",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found during completion sync",
            )

        if response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation service rejected internal authentication during "
                    "completion sync. Check INTERNAL_SERVICE_TOKEN."
                ),
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation service returned an unexpected error during "
                    "completion sync."
                ),
            )


invitation_service_client = InvitationServiceClient()