import pytest
from sqlalchemy import delete

from app.clients.campaign_service_client import campaign_service_client
from app.clients.invitation_service_client import invitation_service_client
from app.db import Base, SessionLocal, engine
from app.models.interview_message import InterviewMessage
from app.models.interview_report import InterviewReport
from app.models.interview_session import InterviewSession
from app.models.interview_structured_answer import InterviewStructuredAnswer


@pytest.fixture(scope="session", autouse=True)
def create_test_tables() -> None:
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with SessionLocal() as session:
        session.execute(delete(InterviewReport))
        session.execute(delete(InterviewStructuredAnswer))
        session.execute(delete(InterviewMessage))
        session.execute(delete(InterviewSession))
        session.commit()


@pytest.fixture(autouse=True)
def mock_service_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_invitation_by_token(invite_token: str) -> dict:
        if not invite_token.startswith("tok_"):
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        suffix = invite_token.replace("tok_", "")[:12] or "demo"
        return {
            "invitationId": f"inv_{suffix}",
            "campaignId": "camp_demo_interview",
            "tenantId": "tenant-dev",
            "recipientEmail": "demo@empresa.com",
            "status": "sent",
            "inviteToken": invite_token,
        }

    def fake_mark_invitation_completed(invitation_id: str) -> None:
        return None

    def fake_get_interview_config(campaign_id: str, tenant_id: str) -> dict:
        return {
            "campaignId": campaign_id,
            "campaignName": "Diagnóstico Comercial Q2",
            "questions": [
                {
                    "id": "main_problem",
                    "text": "¿Cuál es el principal desafío que enfrentas hoy en este proceso?",
                    "objective": "Entender el problema principal.",
                },
                {
                    "id": "problem_quantification",
                    "text": "¿Ese problema está cuantificado?",
                    "objective": "Entender magnitud y frecuencia.",
                },
                {
                    "id": "problem_hypothesis",
                    "text": "¿Cuál crees que es la principal causa del problema?",
                    "objective": "Entender hipótesis de causa raíz.",
                },
                {
                    "id": "expected_results",
                    "text": "¿Qué resultado esperas conseguir al final de este proyecto?",
                    "objective": "Entender expectativa de valor.",
                },
            ],
        }

    monkeypatch.setattr(
        invitation_service_client,
        "get_invitation_by_token",
        fake_get_invitation_by_token,
    )
    monkeypatch.setattr(
        invitation_service_client,
        "mark_invitation_completed",
        fake_mark_invitation_completed,
    )
    monkeypatch.setattr(
        campaign_service_client,
        "get_interview_config",
        fake_get_interview_config,
    )