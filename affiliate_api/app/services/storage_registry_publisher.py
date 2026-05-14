"""
Storage Registry Publisher — data-residency-api integration.

Writes this service's registration blob to shared Redis under
``storage_apis:<api_name>`` at startup and refreshes it every
HEARTBEAT_INTERVAL seconds so data-residency-api can discover it.

The module-level globals DEPLOYMENT_REGION and PRODUCT are intentionally
mutable: the /storage-registry/register endpoint overrides them at runtime,
and subsequent heartbeats pick up the new values automatically.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

# Module-level state — mutated by StorageRegistryPublisher.register()
API_NAME: str = settings.API_NAME
DEPLOYMENT_REGION: str = settings.DEPLOYMENT_REGION
PRODUCT: str = settings.PRODUCT

KEY_TTL_SECONDS: int = 300        # 5 minutes — data-residency-api evicts stale entries
HEARTBEAT_INTERVAL: int = 120     # 2 minutes — keep TTL refreshed


class StorageRegistryPublisher:
    """Publishes and maintains this service's registration in shared Redis."""

    def __init__(self) -> None:
        self._key = f"storage_apis:{API_NAME}"
        self._task: asyncio.Task | None = None

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @property
    def _payload(self) -> dict:
        """Build the current registration payload (reads globals on every call)."""
        return {
            "api_name": API_NAME,
            "region": DEPLOYMENT_REGION,
            "product": PRODUCT,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _write(self, payload: dict) -> None:
        await redis_service.set(self._key, json.dumps(payload), expire=KEY_TTL_SECONDS)

    async def _heartbeat_loop(self) -> None:
        while True:
            try:
                await self._write(self._payload)
                logger.debug("[storage_registry] heartbeat written → %s", self._key)
            except Exception as exc:
                logger.warning("[storage_registry] heartbeat failed: %s", exc)
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        """Write initial registration and start the heartbeat loop."""
        try:
            await self._write(self._payload)
            logger.info(
                "📦 [storage_registry] registered → key=%s region=%s product=%s",
                self._key, DEPLOYMENT_REGION, PRODUCT,
            )
        except Exception as exc:
            logger.error("[storage_registry] initial registration failed: %s", exc)

        self._task = asyncio.create_task(self._heartbeat_loop(), name="storage_registry_heartbeat")

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[storage_registry] heartbeat stopped")

    # ------------------------------------------------------------------ #
    # Self-service API (called by the /storage-registry router)
    # ------------------------------------------------------------------ #

    def get_state(self) -> dict:
        """Snapshot of what the next heartbeat will write to Redis.

        Used by GET /storage-registry."""
        return {
            "api_name": API_NAME,
            "region": DEPLOYMENT_REGION,
            "product": PRODUCT,
            "key": self._key,
            "ttl_seconds": KEY_TTL_SECONDS,
            "heartbeat_interval_seconds": HEARTBEAT_INTERVAL,
        }

    async def register(
        self,
        *,
        region: str,
        product: str,
        metadata: dict | None = None,
    ) -> dict:
        """Override in-memory region/product and immediately write to Redis.

        Subsequent heartbeats keep publishing the new values.
        For permanent changes, also update .env and restart the service.

        Used by POST /storage-registry/register."""
        global DEPLOYMENT_REGION, PRODUCT
        DEPLOYMENT_REGION = region
        PRODUCT = product

        payload = {
            "api_name": API_NAME,
            "region": DEPLOYMENT_REGION,
            "product": PRODUCT,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            payload["metadata"] = metadata

        try:
            await self._write(payload)
            logger.info(
                "[storage_registry] manually registered %s → region=%s product=%s metadata=%s",
                self._key, region, product, "yes" if metadata else "no",
            )
        except Exception as exc:
            logger.error("[storage_registry] manual register failed: %s", exc)
            raise

        return self.get_state()


# Module-level singleton used by the router and main.py
_publisher = StorageRegistryPublisher()
