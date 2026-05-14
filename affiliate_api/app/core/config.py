from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/affiliate_db"
    REDIS_URL: str = "redis://localhost:6379"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_AUDIT_LOGS_TOPIC: str = "affiliate-logs"
    IPINFO_TOKEN: str = ""
    JWT_SECRET_KEY: str = "changeme"

settings = Settings()
