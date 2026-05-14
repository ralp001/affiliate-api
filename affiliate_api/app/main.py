# Source: AffiliateMarketing.API/Program.cs
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Dict, Any
from app.api.routers import dashboard, links, tracking, admin, users, products, resources
from app.core.config import settings
from app.services.redis_service import redis_service
from app.events.kafka_client import get_kafka_client
from app.events.message_bus import initialize_message_bus, get_message_bus
from app.events.permission_consumer import start_permission_consumer, stop_permission_consumer
from app.core.permissions import permission_cache
from app.core.security import require_support_admin

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    try:
        await redis_service.connect()

        kafka_client = get_kafka_client()
        service_id = settings.API_NAME.lower().replace(" ", "-")
        kafka_config = await kafka_client.fetch_config(service_id)
        await initialize_message_bus(kafka_config)

        logger.info("✅ %s initialised with Kafka (SASL/SCRAM-512)", settings.API_NAME)
    except Exception as e:
        logger.warning("⚠️ Kafka/Redis init failed (%s) — API starts without event bus", e)

    await start_permission_consumer()
    logger.info("Starting Affiliate FastAPI...")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    await stop_permission_consumer()
    bus = get_message_bus()
    if bus:
        await bus.disconnect()
    await redis_service.disconnect()
    logger.info("🔌 %s shutdown complete.", settings.API_NAME)

app = FastAPI(
    title="Emutare Affiliate API",
    version="1.0",
    root_path="/affiliate",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(links.router)
app.include_router(tracking.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(resources.router)


@app.get("/affiliate/api/v1/debug/permissions", tags=["Debug"], include_in_schema=False)
async def debug_permissions(_: Dict[str, Any] = Depends(require_support_admin)):
    """[SupportAdmin only] Inspect the in-memory permission cache."""
    return permission_cache.snapshot()

