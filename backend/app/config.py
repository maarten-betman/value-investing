from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = (
        "postgresql+asyncpg://valueinvesting:changeme@localhost:5432/valueinvesting"
    )
    database_url_sync: str = (
        "postgresql://valueinvesting:changeme@localhost:5432/valueinvesting"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-this-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Financial Modeling Prep
    fmp_api_key: str = ""
    fmp_base_url: str = "https://financialmodelingprep.com/api/v3"

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://ollama:11434"

    # Scheduler
    scheduler_timezone: str = "Europe/Amsterdam"

    # Jupyter
    jupyter_token: str = "change-this-to-a-random-token"


settings = Settings()
