from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Interview Service"
    app_version: str = "0.1.0"
    app_env: str = "dev"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    campaign_service_base_url: str = "http://localhost:8001"
    invitation_service_base_url: str = "http://localhost:8002"
    internal_service_token: str = "dev-internal-token"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()