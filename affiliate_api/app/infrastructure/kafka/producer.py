# Source: AffiliateMarketing.Infrastructure/Messaging/KafkaProducerService.cs
import json
from aiokafka import AIOKafkaProducer
from app.core.config import settings

_producer: AIOKafkaProducer | None = None

async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        await _producer.start()
    return _producer

async def stop_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None

async def publish(topic: str, event: dict):
    producer = await get_producer()
    await producer.send_and_wait(topic, event)
