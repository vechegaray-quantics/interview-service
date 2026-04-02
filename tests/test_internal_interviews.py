from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def test_get_internal_interview_by_invitation_returns_transcript_and_report() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_internal_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Problema principal"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Impacta todos los días"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Creemos que es falta de coordinación"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Esperamos reducir tiempos"})
    client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": True},
    )

    response = client.get(
        "/internal/v1/interviews/by-invitation/inv_internal_001",
        headers={"X-Internal-Service-Token": settings.internal_service_token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sessionId"] == session_id
    assert body["invitationId"] == "inv_internal_001"
    assert body["status"] == "completed"
    assert len(body["transcript"]) > 0
    assert len(body["structuredAnswers"]) > 0
    assert body["report"] is not None


def test_get_internal_interview_by_invitation_rejects_invalid_internal_token() -> None:
    response = client.get(
        "/internal/v1/interviews/by-invitation/inv_anything",
        headers={"X-Internal-Service-Token": "wrong-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid internal service token"