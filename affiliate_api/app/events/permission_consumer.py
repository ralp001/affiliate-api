"""
Permission Emission System — Kafka Consumer
Subscribes to {API_NAME}-permissions and permission-updates topics.
Feeds incoming events into the in-memory PermissionCache.
"""
import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from app.core.config import settings
from app.core.permissions import handle_permission_event

logger = logging.getLogger(__name__)

_consumer_task: asyncio.Task | None = None


async def _run_consumer():
    api_topic = f"{settings.API_NAME}-permissions"
    global_topic = "permission-updates"

    while True:
        consumer = AIOKafkaConsumer(
            api_topic,
            global_topic,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=f"{settings.API_NAME}-permission-consumer",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        try:
            await consumer.start()
            logger.info(
                "Permission consumer started — topics: [%s, %s]", api_topic, global_topic
            )
            async for message in consumer:
                try:
                    await handle_permission_event(message.value)
                except Exception as exc:
                    logger.error("Error handling permission event: %s", exc)
        except KafkaConnectionError as exc:
            logger.warning("Permission consumer: Kafka unavailable (%s) — retrying in 30s", exc)
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("Permission consumer cancelled.")
            break
        except Exception as exc:
            logger.error("Permission consumer unexpected error: %s — retrying in 30s", exc)
            await asyncio.sleep(30)
        finally:
            try:
                await consumer.stop()
            except Exception:
                pass


async def start_permission_consumer():
    """Start the permission consumer as a background asyncio task."""
    global _consumer_task
    _consumer_task = asyncio.create_task(_run_consumer())
    logger.info("Permission consumer task created.")


async def stop_permission_consumer():
    """Cancel the background consumer task gracefully."""
    global _consumer_task
    if _consumer_task and not _consumer_task.done():
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
    _consumer_task = None
    logger.info("Permission consumer stopped.")
