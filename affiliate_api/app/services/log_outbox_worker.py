"""
Log Outbox Worker — drains the in-process queue and delivers each UserActionLog to Kafka.
Exponential backoff (2^n seconds) up to max_retries=5.
"""
import asyncio
import logging
import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.core.config import settings
from app.models.log_model import UserActionLog

logger = logging.getLogger(__name__)


class LogOutboxWorker:
    def __init__(self, queue: asyncio.Queue, max_retries: int = 5):
        self.queue = queue
        self.max_retries = max_retries
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.task = asyncio.create_task(self._loop())
        logger.info("📋 Log outbox worker started")

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("📋 Log outbox worker stopped")

    async def _loop(self) -> None:
        while self.running:
            try:
                log_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._process(log_id)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Log outbox worker loop error: %s", exc)

    async def _process(self, log_id: uuid.UUID) -> None:
        async with AsyncSessionLocal() as db:
            entry = await self._get(db, log_id)
            if not entry or entry.synced_to_kafka:
                return

            if entry.retry_count >= self.max_retries:
                logger.warning("Log %s exceeded max retries", log_id)
                return

            if await self._send(entry):
                await db.execute(
                    update(UserActionLog)
                    .where(UserActionLog.id == log_id)
                    .values(synced_to_kafka=True)
                )
                await db.commit()
                logger.debug("Log %s synced to Kafka", log_id)
            else:
                new_count = entry.retry_count + 1
                await db.execute(
                    update(UserActionLog)
                    .where(UserActionLog.id == log_id)
                    .values(retry_count=new_count)
                )
                await db.commit()
                delay = 2 ** entry.retry_count
                logger.info("Log %s retry %d in %ds", log_id, new_count, delay)
                asyncio.create_task(self._delayed_requeue(log_id, delay))

    async def _get(self, db: AsyncSession, log_id: uuid.UUID) -> Optional[UserActionLog]:
        try:
            result = await db.execute(select(UserActionLog).where(UserActionLog.id == log_id))
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error("Failed to fetch log %s: %s", log_id, exc)
            return None

    async def _send(self, entry: UserActionLog) -> bool:
        try:
            from app.events.message_bus import get_message_bus
            bus = get_message_bus()
            if not bus:
                return False

            payload = {
                "id": str(entry.id),
                "user_id": str(entry.user_id) if entry.user_id else None,
                "email": entry.email,
                "responsibility_category": entry.responsibility_category,
                "action": entry.action.value,
                "status": entry.status.value,
                "failure_reason": entry.failure_reason.value if entry.failure_reason else None,
                "ip_address": entry.ip_address,
                "location": entry.location,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                "service": settings.API_NAME,
            }
            topic = settings.KAFKA_USER_ACTION_LOGS_TOPIC
            return await bus.emit(topic, payload, key=str(entry.id))
        except Exception as exc:
            logger.error("Kafka emit failed for log %s: %s", entry.id, exc)
            return False

    async def _delayed_requeue(self, log_id: uuid.UUID, delay: int) -> None:
        await asyncio.sleep(delay)
        try:
            await self.queue.put(log_id)
        except Exception as exc:
            logger.error("Failed to requeue log %s: %s", log_id, exc)


async def start_log_outbox_worker(queue: asyncio.Queue, max_retries: int = 5) -> LogOutboxWorker:
    worker = LogOutboxWorker(queue, max_retries)
    await worker.start()
    return worker
