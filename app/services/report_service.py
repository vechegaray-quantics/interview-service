from datetime import UTC, datetime

from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession


class ReportService:
    def build_report(
        self,
        session_obj: InterviewSession,
        campaign: dict,
        messages: list[InterviewMessage],
        include_transcript: bool,
    ) -> dict:
        user_messages = [
            message.content.strip()
            for message in messages
            if message.role == "user" and message.content.strip()
        ]

        transcript = []
        if include_transcript:
            transcript = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

        summary = (
            f"Se completó una entrevista para la campaña {campaign['campaignName']} "
            f"con {len(user_messages)} respuesta(s) registradas."
        )

        main_problem = (
            user_messages[0]
            if user_messages
            else "No se registraron respuestas suficientes para identificar un problema principal."
        )

        observed_symptoms = user_messages[1:3]
        known_impact = user_messages[3:4]

        return {
            "metadata": {
                "sessionId": session_obj.session_id,
                "version": "v1",
                "generatedAt": datetime.now(UTC).isoformat(),
                "campaignId": session_obj.campaign_id,
                "campaignName": campaign["campaignName"],
                "model": "stub-v1",
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