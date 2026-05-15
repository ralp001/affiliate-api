from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Resolve .env relative to this file so it is found regardless of working directory
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
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
    # Multi-tenant JWT — one secret per issuer
    INTERNAL_AUTH_JWT_SECRET: str = ""
    EXTERNAL_AUTH_JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    # API identification
    API_NAME: str = "affiliate-marketing-api"
    API_KEY: str = ""
    # API-Manager
    API_MANAGER_URL: str = "http://34.70.122.249:8000"
    # Kafka topics
    KAFKA_USER_EVENTS_TOPIC: str = "user-events"
    KAFKA_API_DATA_TYPES_TOPIC: str = "api-data-types"
    KAFKA_PERMISSION_UPDATES_TOPIC: str = "permission-updates"
    KAFKA_SECURITY_LOGS_TOPIC: str = "security-logs"
    KAFKA_USER_ACTION_LOGS_TOPIC: str = "user-action-logs"
    # Auth bypass (set DISABLE_AUTH=true in .env to skip JWT checks — demo/testing only)
    DISABLE_AUTH: bool = False
    # Logging system
    LOG_OUTBOX_QUEUE_SIZE: int = 1000
    LOG_MAX_RETRY_COUNT: int = 5
    # Redis
    REDIS_HOST: str = "34.70.122.249"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    # Storage registry (data-residency-api integration)
    DEPLOYMENT_REGION: str = "us"
    PRODUCT: str = "idex"

settings = Settings()
