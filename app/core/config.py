from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    app_env: str = "dev"

    database_url: str
    internal_service_token: str
    campaign_service_base_url: str
    invitation_service_base_url: str

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_max_followups_per_question: int = 1
    llm_followup_temperature: float = 0.2
    llm_followup_timeout_seconds: int = 20


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