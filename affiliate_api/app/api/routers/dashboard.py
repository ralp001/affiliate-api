# Source: AffiliateMarketing.API/Controllers/AffiliateDashboardController.cs
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services import dashboard_service
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.affiliate import SimulateSaleRequest
from app.infrastructure.kafka.log_service import KafkaLogService

router = APIRouter(prefix="/affiliate/api/v1/dashboard", tags=["02. Affiliate Performance Dashboard"])
log_service = KafkaLogService()

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(db: AsyncSession = Depends(get_db)):
    await log_service.log(None, "View_Dashboard", "Success", "User viewed performance stats.")
    return await dashboard_service.get_summary(db)

@router.post("/simulate-sale")
async def simulate_sale(request: SimulateSaleRequest, db: AsyncSession = Depends(get_db)):
    from app.models.conversion import Conversion
    from app.models.referral_link import ReferralLink
    from sqlalchemy import select
    result = await db.execute(select(ReferralLink).where(ReferralLink.generated_code == request.referral_code))
    link = result.scalar_one_or_none()
    if not link:
        return {"error": "Invalid Referral Code or Product ID."}
    conversion = Conversion(
        affiliate_user_id=link.affiliate_profile_id,
        buyer_user_id=link.affiliate_profile_id,
        product_id=request.product_id,
        sale_amount=request.sale_amount,
        commission_earned=0,
        referral_code=request.referral_code,
    )
    db.add(conversion)
    await db.commit()
    return {"message": "Sale Simulated Successfully. Refresh dashboard to see updates."}
