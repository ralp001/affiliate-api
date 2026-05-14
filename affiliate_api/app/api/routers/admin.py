# Source: AffiliateMarketing.API/Controllers/AdminManagementController.cs
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.models.audit_log import AuditLog
from app.infrastructure.kafka.log_service import KafkaLogService

router = APIRouter(prefix="/affiliate/api/v1/admin", tags=["05. System Administration"])
log_service = KafkaLogService()

@router.put("/commission-rate")
async def update_commission_rate(new_rate: float):
    await log_service.log(None, "Update_Global_Commission", "Success", f"Commission rate updated to {new_rate}%")
    return {"message": "Global commission rate updated successfully"}

@router.get("/audit-logs/{entity_name}")
async def get_audit_logs(entity_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_name == entity_name)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    )
    logs = result.scalars().all()
    return logs
