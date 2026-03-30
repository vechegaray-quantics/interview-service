import json

import httpx

from app.core.config import settings


class OpenAIFollowUpClient:
    def generate_follow_up_question(
        self,
        *,
        question_text: str,
        question_objective: str,
        user_answer: str,
        previous_follow_up_count: int,
        max_follow_up_questions: int,
    ) -> str | None:
        if not settings.openai_api_key:
            return None

        prompt = (
            "Eres un asistente de entrevistas en español. "
            "Evalúa si la respuesta del usuario requiere profundización antes de continuar. "
            "Si se requiere follow-up, responde SOLAMENTE en JSON con la forma: "
            '{"shouldFollowUp": true, "followUpQuestion": "..."}. '
            "Si no se requiere, responde: "
            '{"shouldFollowUp": false}. '
            "No agregues texto extra fuera del JSON."
        )

        payload = {
            "model": settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                f"Pregunta actual: {question_text}\n"
                                f"Objetivo de la pregunta: {question_objective}\n"
                                f"Respuesta del usuario: {user_answer}\n"
                                f"Follow-ups ya realizados: {previous_follow_up_count}\n"
                                f"Máximo de follow-ups permitidos: {max_follow_up_questions}\n"
                                "Solo sugiere follow-up si la respuesta es ambigua, incompleta, "
                                "contradictoria o sugiere riesgo importante sin detalle."
                            ),
                        }
                    ],
                },
            ],
            "max_output_tokens": 200,
            "temperature": 0.2,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code >= 400:
            return None

        data = response.json()
        output_text = data.get("output_text", "").strip()
        if not output_text:
            return None

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError:
            return None

        should_follow_up = bool(parsed.get("shouldFollowUp"))
        follow_up_question = (parsed.get("followUpQuestion") or "").strip()
        if not should_follow_up or not follow_up_question:
            return None

        return follow_up_question


openai_followup_client = OpenAIFollowUpClient()
