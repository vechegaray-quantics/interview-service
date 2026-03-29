from fastapi.testclient import TestClient

from app.clients.invitation_service_client import invitation_service_client
from app.main import app


client = TestClient(app)


def test_start_interview_returns_session_and_first_question() -> None:
    response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_demo_001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sessionId"].startswith("sess_")
    assert body["campaignId"] == "camp_demo_interview"
    assert body["campaignName"] == "Diagnóstico Comercial Q2"
    assert body["sessionCompleted"] is False
    assert "principal desafío" in body["assistantMessage"]


def test_start_interview_is_idempotent_for_same_token() -> None:
    first = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_same_001"},
    )
    second = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_same_001"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["sessionId"] == second.json()["sessionId"]


def test_get_interview_session_returns_existing_session() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_existing_001"},
    )
    session_id = start_response.json()["sessionId"]

    response = client.get(f"/public/v1/interviews/{session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["sessionId"] == session_id
    assert body["campaignId"] == "camp_demo_interview"
    assert body["sessionCompleted"] is False


def test_start_interview_returns_not_found_for_invalid_token() -> None:
    response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "invalid_token"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invitation not found"


def test_post_message_advances_to_next_question() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_turn_001"},
    )
    session_id = start_response.json()["sessionId"]

    response = client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Tenemos retrasos frecuentes en la operación."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sessionCompleted"] is False
    assert "cuantificado" in body["assistantMessage"]


def test_post_message_marks_session_completed_after_last_question() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_finish_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Respuesta 1"},
    )
    client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Respuesta 2"},
    )
    client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Respuesta 3"},
    )
    final_response = client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Respuesta 4"},
    )

    assert final_response.status_code == 200
    body = final_response.json()
    assert body["sessionCompleted"] is True
    assert "lista para finalizar" in body["assistantMessage"]


def test_post_message_returns_not_found_for_unknown_session() -> None:
    response = client.post(
        "/public/v1/interviews/sess_unknown/messages",
        json={"message": "Hola"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview session not found"


def test_finalize_returns_report_when_session_is_ready() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_finalize_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Problema principal"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Impacta todos los días"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Creemos que es falta de coordinación"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Esperamos reducir tiempos"})

    response = client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["report"]["metadata"]["sessionId"] == session_id
    assert body["report"]["metadata"]["version"] == "v1"
    assert body["report"]["mainProblem"] == "Problema principal"
    assert len(body["report"]["transcript"]) > 0


def test_finalize_is_idempotent() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_finalize_same_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 1"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 2"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 3"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 4"})

    first = client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": True},
    )
    second = client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": True},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_finalize_returns_conflict_if_session_is_not_ready() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_not_ready_001"},
    )
    session_id = start_response.json()["sessionId"]

    response = client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": False},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Interview session is not ready to finalize"


def test_post_message_returns_conflict_after_finalize() -> None:
    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_after_finalize_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 1"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 2"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 3"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 4"})
    client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": False},
    )

    response = client.post(
        f"/public/v1/interviews/{session_id}/messages",
        json={"message": "Otra respuesta"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Interview session is already completed"


def test_finalize_marks_invitation_completed(monkeypatch) -> None:
    completed_calls: list[str] = []

    def fake_mark_completed(invitation_id: str) -> None:
        completed_calls.append(invitation_id)

    monkeypatch.setattr(
        invitation_service_client,
        "mark_invitation_completed",
        fake_mark_completed,
    )

    start_response = client.post(
        "/public/v1/interviews/start",
        json={"inviteToken": "tok_mark_001"},
    )
    session_id = start_response.json()["sessionId"]

    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 1"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 2"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 3"})
    client.post(f"/public/v1/interviews/{session_id}/messages", json={"message": "Respuesta 4"})

    response = client.post(
        f"/public/v1/interviews/{session_id}/finalize",
        json={"includeTranscript": False},
    )

    assert response.status_code == 200
    assert completed_calls == ["inv_mark_001"]