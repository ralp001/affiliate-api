"""
Permission Emission System — Kafka Consumer
Subscribes to {API_NAME}-permissions and permission-updates topics.
Feeds incoming events into the in-memory PermissionCache.
"""
import asyncio
import json
import logging

from app.core.config import settings
from app.core.permissions import handle_permission_event
from app.events.message_bus import get_message_bus

logger = logging.getLogger(__name__)

_consumer_task: asyncio.Task | None = None


async def _run_consumer():
    api_topic = f"{settings.API_NAME}-permissions"
    global_topic = settings.KAFKA_PERMISSION_UPDATES_TOPIC

    while True:
        try:
            bus = get_message_bus()
            if not bus:
                logger.warning("Permission consumer: MessageBus not ready — retrying in 15s")
                await asyncio.sleep(15)
                continue

            consumer = await bus.create_consumer(
                topics=[api_topic, global_topic],
                group_id=f"{settings.API_NAME}-permission-consumer",
            )
            await consumer.start()
            logger.info("Permission consumer started — topics: [%s, %s]", api_topic, global_topic)
            async for message in consumer:
                try:
                    await handle_permission_event(message.value)
                except Exception as exc:
                    logger.error("Error handling permission event: %s", exc)
        except asyncio.CancelledError:
            logger.info("Permission consumer cancelled.")
            break
        except Exception as exc:
            logger.error("Permission consumer error: %s — retrying in 30s", exc)
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
