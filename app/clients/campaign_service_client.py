class CampaignServiceClient:
    def get_interview_config(self, campaign_id: str) -> dict:
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


campaign_service_client = CampaignServiceClient()