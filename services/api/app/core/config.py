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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
