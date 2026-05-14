"""
Kafka Client — fetches SASL credentials from API-Manager with Redis + memory caching.
Memory cache TTL : 5 min
Redis cache TTL  : 24 h
"""
import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class KafkaClient:
    def __init__(self, api_manager_url: str, api_key: str):
        self.api_manager_url = api_manager_url.rstrip("/")
        self.api_key = api_key
        self._cached_config: Optional[Dict[str, Any]] = None
        self._config_expires: float = 0

    def _redis_key(self, service_id: str) -> str:
        return f"kafka_config_cache:{service_id}"

    async def fetch_config(self, service_id: str, force: bool = False) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).timestamp()

        # 1. Memory cache
        if not force and self._cached_config and now < self._config_expires:
            return self._cached_config

        # 2. Redis cache
        if not force:
            try:
                cached = await redis_service.get(self._redis_key(service_id))
                if cached:
                    config = json.loads(cached)
                    self._cached_config = config
                    self._config_expires = now + 300
                    logger.debug("💾 Kafka config for %s loaded from Redis", service_id)
                    return config
            except Exception as e:
                logger.warning("⚠️ Redis cache miss/error for %s: %s", service_id, e)

        # 3. API-Manager
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_manager_url}/api/v1/apis/kafka/config/{service_id}"
                headers = {"X-API-Key": self.api_key}
                logger.info("🔑 Fetching Kafka credentials from API-Manager for %s", service_id)
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        config = await resp.json()
                        self._cached_config = config
                        self._config_expires = now + 300
                        try:
                            await redis_service.set(
                                self._redis_key(service_id), json.dumps(config), expire=86400
                            )
                            logger.info("✅ Kafka config for %s cached in Redis", service_id)
                        except Exception as re:
                            logger.warning("⚠️ Failed to update Redis cache: %s", re)
                        return config
                    else:
                        err = await resp.text()
                        logger.error("❌ API-Manager returned %s: %s", resp.status, err)
                        raise Exception(f"API-Manager error {resp.status}: {err}")
        except Exception as e:
            logger.error("❌ Connection error to API-Manager: %s", e)
            raise

    async def invalidate_cache(self, service_id: str):
        self._cached_config = None
        self._config_expires = 0
        try:
            await redis_service.delete(self._redis_key(service_id))
            logger.info("🧹 Caches invalidated for %s", service_id)
        except Exception as e:
            logger.error("❌ Failed to invalidate Redis cache: %s", e)


_client: Optional[KafkaClient] = None


def get_kafka_client() -> KafkaClient:
    global _client
    if not _client:
        if not settings.API_KEY:
            raise ValueError("API_KEY must be set in .env")
        _client = KafkaClient(
            api_manager_url=settings.API_MANAGER_URL,
            api_key=settings.API_KEY,
        )
    return _client
