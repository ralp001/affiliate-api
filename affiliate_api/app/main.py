# Source: AffiliateMarketing.API/Program.cs
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Dict, Any
from app.api.routers import dashboard, links, tracking, admin, users, products, resources
from app.routers.storage_registry import router as storage_registry_router
from app.services.storage_registry_publisher import _publisher as storage_registry_publisher
from app.core.config import settings
from app.services.redis_service import redis_service
from app.events.kafka_client import get_kafka_client
from app.events.message_bus import initialize_message_bus, get_message_bus
from app.events.permission_consumer import start_permission_consumer, stop_permission_consumer
from app.services.log_queue import set_log_queue
from app.services.log_outbox_worker import start_log_outbox_worker
from app.core.permissions import permission_cache
from app.core.security import require_support_admin

logger = logging.getLogger(__name__)


async def _emergency_recovery(queue: asyncio.Queue) -> None:
    """Re-queue any unsynced logs left over from a previous crash."""
    try:
        from sqlalchemy import select
        from app.core.db import AsyncSessionLocal
        from app.models.log_model import UserActionLog
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(UserActionLog)
                .where(UserActionLog.synced_to_kafka == False)  # noqa: E712
                .where(UserActionLog.retry_count < settings.LOG_MAX_RETRY_COUNT)
                .order_by(UserActionLog.timestamp)
            )
            unsynced = result.scalars().all()
            if unsynced:
                logger.info("🔄 Emergency recovery: queueing %d unsynced logs", len(unsynced))
                for entry in unsynced:
                    await queue.put(entry.id)
    except Exception as exc:
        logger.error("Emergency recovery failed: %s", exc)


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

    # ── Storage registry (data-residency-api) ────────────────────────────────
    try:
        await storage_registry_publisher.start()
    except Exception as exc:
        logger.warning("⚠️ Storage registry publisher failed to start: %s", exc)

    # ── Log queue + outbox worker ─────────────────────────────────────────────
    try:
        log_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.LOG_OUTBOX_QUEUE_SIZE)
        set_log_queue(log_queue)
        app.state.log_worker = await start_log_outbox_worker(
            log_queue, max_retries=settings.LOG_MAX_RETRY_COUNT
        )
        await _emergency_recovery(log_queue)
        logger.info("📋 Log queue and outbox worker ready")
    except Exception as exc:
        logger.error("Failed to start log outbox worker: %s", exc)

    logger.info("Starting Affiliate FastAPI...")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    if hasattr(app.state, "log_worker"):
        await app.state.log_worker.stop()
    await storage_registry_publisher.stop()
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
app.include_router(storage_registry_router)


@app.get("/affiliate/api/v1/debug/permissions", tags=["Debug"], include_in_schema=False)
async def debug_permissions(_: Dict[str, Any] = Depends(require_support_admin)):
    """[SupportAdmin only] Inspect the in-memory permission cache."""
    return permission_cache.snapshot()

