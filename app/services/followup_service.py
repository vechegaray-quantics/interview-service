import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.models.interview_message import InterviewMessage


class FollowUpService:
    def __init__(self) -> None:
        self._client: OpenAI | None = None
        if settings.openai_api_key.strip():
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.llm_followup_timeout_seconds,
            )

    def decide_follow_up(
        self,
        *,
        campaign_name: str,
        question_text: str,
        question_objective: str,
        thread_messages: list[InterviewMessage],
        follow_up_count: int,
        max_follow_ups: int,
    ) -> dict[str, Any]:
        if self._client is None:
            return self._no_follow_up("OPENAI_API_KEY no configurada")

        if follow_up_count >= max_follow_ups:
            return self._no_follow_up("Límite de follow-ups alcanzado")

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            campaign_name=campaign_name,
            question_text=question_text,
            question_objective=question_objective,
            thread_messages=thread_messages,
            follow_up_count=follow_up_count,
            max_follow_ups=max_follow_ups,
        )

        schema = {
            "type": "object",
            "properties": {
                "requiresFollowUp": {"type": "boolean"},
                "followUpQuestion": {"type": ["string", "null"]},
                "reason": {"type": "string"},
            },
            "required": ["requiresFollowUp", "followUpQuestion", "reason"],
            "additionalProperties": False,
        }

        try:
            response = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.llm_followup_temperature,
                max_tokens=250,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "follow_up_decision",
                        "strict": True,
                        "schema": schema,
                    },
                },
            )

            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)
        except Exception as exc:
            return self._no_follow_up(f"Fallo consultando LLM: {exc}")

        requires_follow_up = bool(parsed.get("requiresFollowUp"))
        follow_up_question = parsed.get("followUpQuestion")
        reason = str(parsed.get("reason", "")).strip() or "Sin motivo informado por el LLM"

        if not requires_follow_up:
            return self._no_follow_up(reason)

        if not isinstance(follow_up_question, str) or not follow_up_question.strip():
            return self._no_follow_up("El LLM indicó seguimiento, pero no devolvió una pregunta válida")

        return {
            "requiresFollowUp": True,
            "followUpQuestion": follow_up_question.strip(),
            "reason": reason,
        }

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "Eres un entrevistador experto en investigación cualitativa. "
            "Tu trabajo es decidir si hace falta UNA repregunta breve para profundizar "
            "en la pregunta base actual. "
            "Solo debes pedir seguimiento si la última respuesta del usuario fue vaga, "
            "incompleta, ambigua, contradictoria o insuficiente para cumplir el objetivo "
            "de la pregunta. "
            "No repitas la pregunta base. "
            "No hagas más de una pregunta en la misma intervención. "
            "No inventes hechos. "
            "Si la respuesta ya es suficiente, devuelve requiresFollowUp=false."
        )

    @staticmethod
    def _build_user_prompt(
        *,
        campaign_name: str,
        question_text: str,
        question_objective: str,
        thread_messages: list[InterviewMessage],
        follow_up_count: int,
        max_follow_ups: int,
    ) -> str:
        thread_text = FollowUpService._format_thread(thread_messages)

        return (
            f"CAMPAÑA: {campaign_name}\n"
            f"PREGUNTA BASE: {question_text}\n"
            f"OBJETIVO DE LA PREGUNTA: {question_objective}\n"
            f"FOLLOW-UPS YA HECHOS EN ESTA PREGUNTA: {follow_up_count}\n"
            f"MAXIMO DE FOLLOW-UPS PERMITIDOS: {max_follow_ups}\n\n"
            f"HISTORIAL DEL TEMA:\n{thread_text}\n\n"
            "Devuelve JSON estricto con:\n"
            "- requiresFollowUp: boolean\n"
            "- followUpQuestion: string|null\n"
            "- reason: string\n\n"
            "La follow-up question debe ser abierta, natural, corta y útil."
        )

    @staticmethod
    def _format_thread(messages: list[InterviewMessage]) -> str:
        if not messages:
            return "(sin historial)"

        lines: list[str] = []
        for message in messages:
            role = "Agente" if message.role == "assistant" else "Usuario"
            lines.append(f"{role}: {message.content}")

        return "\n".join(lines)

    @staticmethod
    def _no_follow_up(reason: str) -> dict[str, Any]:
        return {
            "requiresFollowUp": False,
            "followUpQuestion": None,
            "reason": reason,
        }


followup_service = FollowUpService()