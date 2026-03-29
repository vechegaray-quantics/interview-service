from datetime import UTC, datetime

from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession
from app.models.interview_structured_answer import InterviewStructuredAnswer


class ReportService:
    def build_report(
        self,
        session_obj: InterviewSession,
        campaign: dict,
        messages: list[InterviewMessage],
        structured_answers: list[InterviewStructuredAnswer],
        include_transcript: bool,
    ) -> dict:
        transcript = []
        if include_transcript:
            transcript = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

        ordered_answers = [answer.answer_text.strip() for answer in structured_answers if answer.answer_text.strip()]

        main_problem = (
            ordered_answers[0]
            if ordered_answers
            else "No se registraron respuestas suficientes para identificar un problema principal."
        )

        observed_symptoms = ordered_answers[1:3]
        known_impact = ordered_answers[3:4]

        summary = (
            f"Se completó una entrevista para la campaña {campaign['campaignName']} "
            f"con {len(ordered_answers)} respuesta(s) estructuradas."
        )

        return {
            "metadata": {
                "sessionId": session_obj.session_id,
                "version": "v1",
                "generatedAt": datetime.now(UTC).isoformat(),
                "campaignId": session_obj.campaign_id,
                "campaignName": campaign["campaignName"],
                "model": "stub-v2-structured",
            },
            "summary": summary,
            "mainProblem": main_problem,
            "observedSymptoms": observed_symptoms,
            "knownImpact": known_impact,
            "openQuestions": [],
            "suggestedNextSteps": [
                "Validar los hallazgos con los stakeholders principales.",
                "Priorizar acciones sobre el problema principal identificado.",
            ],
            "transcript": transcript,
        }


report_service = ReportService()