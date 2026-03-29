from fastapi import HTTPException, status


class InvitationServiceClient:
    def get_invitation_by_token(self, invite_token: str) -> dict:
        token = invite_token.strip()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inviteToken is required",
            )

        if not token.startswith("tok_"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        suffix = token.replace("tok_", "")[:12] or "demo"

        return {
            "invitationId": f"inv_{suffix}",
            "campaignId": "camp_demo_interview",
            "tenantId": "tenant-dev",
            "recipientEmail": "demo@empresa.com",
            "status": "sent",
        }


invitation_service_client = InvitationServiceClient()