from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres"
    internal_service_token: str = "dev-internal-token"
    campaign_service_base_url: str = "http://127.0.0.1:8001"
    invitation_service_base_url: str = "http://127.0.0.1:8002"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    interview_follow_up_max_questions: int = 2
    cors_allowed_origins: str = (
        "http://localhost:8000,"
        "http://127.0.0.1:8000,"
        "https://encuestas-interview.web.app,"
        "https://encuestas-interview.firebaseapp.com,"
        "https://encuestas-490902.web.app,"
        "https://encuestas-490902.firebaseapp.com"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
