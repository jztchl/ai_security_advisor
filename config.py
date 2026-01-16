from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    MISTRAL_API_KEY: str
    REDIS_URL: str
    REDIS_CELERY_BROKER: str

    class Config:
        env_file = ".env"


settings = Settings()
