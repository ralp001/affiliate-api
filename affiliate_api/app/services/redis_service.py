import redis.asyncio as redis
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error("❌ Failed to connect to Redis: %s", e)
            raise

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.aclose()
            logger.info("🔌 Redis connection closed")

    async def get(self, key: str) -> Optional[str]:
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return await self.redis_client.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return await self.redis_client.delete(key) > 0

    async def publish(self, channel: str, message: str) -> int:
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return await self.redis_client.publish(channel, message)

    def pubsub(self):
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        return self.redis_client.pubsub()


redis_service = RedisService()
