import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class CampaignServiceClient:
    def get_interview_config(
        self,
        campaign_id: str,
        tenant_id: str,
    ) -> dict:
        base_url = settings.campaign_service_base_url.rstrip("/")
        url = f"{base_url}/v1/campaigns/{campaign_id}"

        try:
            response = httpx.get(
                url,
                headers={
                    "X-Tenant-Id": tenant_id,
                },
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Campaign service unavailable: {exc}",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found",
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Campaign service returned an unexpected error",
            )

        payload = response.json()
        raw_questions = payload.get("questions") or []

        questions = []
        for index, item in enumerate(raw_questions, start=1):
            question_id = item.get("id") or f"q_{index}"
            question_text = item.get("text", "").strip()
            question_objective = item.get("objective") or question_text

            if question_text:
                questions.append(
                    {
                        "id": question_id,
                        "text": question_text,
                        "objective": question_objective,
                    }
                )

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Campaign interview config has no questions",
            )

        return {
            "campaignId": payload["campaignId"],
            "campaignName": payload.get("campaignName", "Campaign"),
            "questions": questions,
        }


campaign_service_client = CampaignServiceClient()