# Source: AffiliateMarketing.Infrastructure/Logging/KafkaLogService.cs
import uuid
from datetime import datetime, timezone
from app.core.config import settings

class KafkaLogService:
    async def log(self, user_id: uuid.UUID | None, action: str, status: str, message: str = ""):
        entry = {
            "event_type": "AFFILIATE_AUDIT_LOG",
            "source_service": settings.API_NAME,
            "api": "AffiliateMarketing_API",
            "user_id": str(user_id) if user_id else None,
            "action": action,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "Production_VM",
        }
        try:
            from app.events.message_bus import get_message_bus
            bus = get_message_bus()
            if bus:
                await bus.emit(settings.KAFKA_AUDIT_LOGS_TOPIC, entry)
        except Exception:
            # Kafka unavailable — log is silently dropped so the API stays up
            pass
