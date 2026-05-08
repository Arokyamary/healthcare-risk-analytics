from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db"
    SECRET_KEY: str = "your-secret-key-change-in-production-minimum-32-chars"
    ENVIRONMENT: str = "development"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    CORS_ORIGINS: list = ["http://localhost:3000"]
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()