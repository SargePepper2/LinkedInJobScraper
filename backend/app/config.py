from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/jobscraper"
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = False

    model_config = {"env_prefix": "JOBSCAN_", "env_file": ".env"}


settings = Settings()
