"""
SASL/SCRAM-512 Kafka Message Bus with dynamic credential refresh via Redis pub/sub.
"""
import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.config import settings

logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(
        self,
        bootstrap_servers: List[str],
        username: str,
        password: str,
        service_id: str,
        consumer_group_id: Optional[str] = None,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.username = username
        self.password = password
        self.service_id = service_id
        self.consumer_group_id = consumer_group_id or f"{service_id}-group"
        self.producer: Optional[AIOKafkaProducer] = None
        self._connected = False
        self._refresh_task: Optional[asyncio.Task] = None
        self._on_refresh_callbacks: List[Callable[[], Awaitable[None]]] = []

    async def connect(self):
        if self._connected:
            return
        logger.info("📡 Initializing MessageBus: %s as %s", self.bootstrap_servers, self.username)
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                security_protocol="SASL_PLAINTEXT",
                sasl_mechanism="SCRAM-SHA-512",
                sasl_plain_username=self.username,
                sasl_plain_password=self.password,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            )
            await self.producer.start()
            self._connected = True
            logger.info("📡 MessageBus producer connected (SASL/SCRAM-512)")
            if not self._refresh_task:
                self._refresh_task = asyncio.create_task(self._listen_for_config_updates())
        except Exception as e:
            logger.error("❌ Failed to connect producer: %s", e)
            self._connected = False
            raise

    async def _listen_for_config_updates(self):
        from app.services.redis_service import redis_service
        channel = f"kafka_config_updates:{self.service_id}"
        logger.info("📡 Config update listener started on channel: %s", channel)
        try:
            max_retries = 30
            while not getattr(redis_service, "redis_client", None) and max_retries > 0:
                await asyncio.sleep(1)
                max_retries -= 1
            if not getattr(redis_service, "redis_client", None):
                logger.error("❌ Redis not initialised — config update listener aborted")
                return
            pubsub = redis_service.pubsub()
            await pubsub.subscribe(channel)
            logger.info("👂 Listening for credential rotation on: %s", channel)
            async for message in pubsub.listen():
                if message["type"] == "message" and message["data"] in ("REFRESH", b"REFRESH"):
                    logger.warning("🔄 Credential rotation signal received for %s", self.service_id)
                    await self._refresh_credentials()
        except Exception as e:
            logger.error("❌ Config update listener error: %s", e)
            self._refresh_task = None

    async def _refresh_credentials(self):
        try:
            from app.events.kafka_client import get_kafka_client
            config = await get_kafka_client().fetch_config(self.service_id, force=True)
            self.username = config.get("sasl_username") or config.get("username")
            self.password = config.get("sasl_password") or config.get("password")
            servers = config.get("bootstrap_servers", self.bootstrap_servers)
            self.bootstrap_servers = [servers] if isinstance(servers, str) else servers
            logger.info("🔄 Restarting producer with new credentials for %s", self.username)
            if self.producer:
                await self.producer.stop()
                self._connected = False
            await self.connect()
            for cb in self._on_refresh_callbacks:
                try:
                    await cb()
                except Exception as ce:
                    logger.error("❌ Refresh callback error: %s", ce)
            logger.info("✅ Credential rotation complete")
        except Exception as e:
            logger.error("❌ Failed to rotate credentials: %s", e)

    def register_refresh_callback(self, cb: Callable[[], Awaitable[None]]):
        self._on_refresh_callbacks.append(cb)

    async def disconnect(self):
        if self._refresh_task:
            self._refresh_task.cancel()
        if self.producer:
            await self.producer.stop()
            self._connected = False
            logger.info("📡 MessageBus producer disconnected")

    async def create_consumer(
        self, topics: List[str], group_id: Optional[str] = None
    ) -> AIOKafkaConsumer:
        final_group_id = group_id or self.consumer_group_id
        logger.info("📥 Creating consumer for %s (group: %s)", topics, final_group_id)
        return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-512",
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            group_id=final_group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

    async def emit(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        if not self._connected:
            try:
                await self.connect()
            except Exception:
                logger.error("❌ Cannot emit: MessageBus not connected")
                return False
        try:
            await self.producer.send_and_wait(
                topic,
                message,
                key=key.encode("utf-8") if key else None,
            )
            return True
        except Exception as e:
            logger.error("❌ Error emitting to %s: %s", topic, e)
            return False

    async def consume_messages(
        self,
        consumer: AIOKafkaConsumer,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        try:
            async for message in consumer:
                try:
                    await handler(message.value)
                except Exception as e:
                    logger.error("❌ Error processing message: %s", e)
        except Exception as e:
            logger.error("❌ Consumer loop error: %s", e)
        finally:
            await consumer.stop()


_message_bus: Optional[MessageBus] = None


async def initialize_message_bus(config: Dict[str, Any]) -> MessageBus:
    global _message_bus
    # Prefer the externally-reachable bootstrap servers from .env; the API-Manager
    # may return an internal address (e.g. localhost:29092) that only works on its
    # own host.  settings.KAFKA_BOOTSTRAP_SERVERS always points to the correct
    # external host for this deployment.
    env_servers = settings.KAFKA_BOOTSTRAP_SERVERS
    if env_servers:
        servers = [s.strip() for s in env_servers.split(",")]
    else:
        servers = config.get("bootstrap_servers", [])
        if isinstance(servers, str):
            servers = [servers]
    username = config.get("sasl_username") or config.get("username")
    password = config.get("sasl_password") or config.get("password")
    service_id = settings.API_NAME.lower().replace(" ", "-")
    consumer_group_id = config.get("consumer_group_id") or f"{service_id}-group"
    _message_bus = MessageBus(
        bootstrap_servers=servers,
        username=username,
        password=password,
        service_id=service_id,
        consumer_group_id=consumer_group_id,
    )
    logger.info("📡 MessageBus consumer group: %s", consumer_group_id)
    await _message_bus.connect()
    return _message_bus


def get_message_bus() -> Optional[MessageBus]:
    return _message_bus
