from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "reviewdunia-backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    postgres_dsn: str = "postgresql+psycopg2://reviewdunia:reviewdunia@postgres:5432/reviewdunia"
    mongodb_uri: str = "mongodb://mongo:27017"
    mongodb_db_name: str = "reviewdunia"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    upload_volume_path: str = "/data/uploads"
    review_max_iterations: int = 10
    review_target_score: float = 9.6

    copilot_models_api_base_url: str = "https://api.githubcopilot.com/models"
    copilot_models_api_key: str | None = None
    copilot_agent_config_path: str = "services/agents/config/agents.json"
    copilot_request_timeout_seconds: int = 30
    copilot_dry_run: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
