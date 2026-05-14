from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Resolve .env relative to this file so it is found regardless of working directory
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://postgres:cyberrole_2026@localhost:5432/affiliate_db"
    REDIS_URL: str = "redis://localhost:6379"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_AUDIT_LOGS_TOPIC: str = "affiliate-logs"
    IPINFO_TOKEN: str = "aa55f34e25388c"
    # Legacy single-secret (kept for local dev tooling only — not used for auth)
    JWT_SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_BASE_URL: str = "https://abraham-emutare.duckdns.org/affiliate"
    API_NAME: str = "affiliate-marketing-api"
    API_KEY: str = ""
    # Multi-tenant JWT — one secret per issuer
    INTERNAL_AUTH_JWT_SECRET: str = ""
    EXTERNAL_AUTH_JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"

settings = Settings()
