from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_dashboard_interview_by_invitation_returns_transcript_and_report() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_dashboard_001"},
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
        "/v1/interviews/by-invitation/inv_dashboard_001",
        headers={"X-Tenant-Id": "tenant-dev"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sessionId"] == session_id
    assert body["invitationId"] == "inv_dashboard_001"
    assert body["tenantId"] == "tenant-dev"
    assert body["status"] == "completed"
    assert len(body["transcript"]) > 0
    assert len(body["structuredAnswers"]) > 0
    assert body["report"] is not None


def test_get_dashboard_interview_by_invitation_requires_tenant_header() -> None:
    response = client.get(
        "/v1/interviews/by-invitation/inv_anything",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Tenant-Id header is required"


def test_get_dashboard_interview_by_invitation_returns_not_found_for_wrong_tenant() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_dashboard_002"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 1"})

    response = client.get(
        "/v1/interviews/by-invitation/inv_dashboard_002",
        headers={"X-Tenant-Id": "tenant-otro"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview session not found for invitation"