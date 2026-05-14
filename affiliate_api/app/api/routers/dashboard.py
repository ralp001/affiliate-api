# Source: AffiliateMarketing.API/Controllers/AffiliateDashboardController.cs
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import require_support_admin, require_affiliate
from app.services import dashboard_service
from app.schemas.dashboard import DashboardSummaryResponse, MyDashboardResponse
from app.schemas.affiliate import SimulateSaleRequest
from app.infrastructure.kafka.log_service import KafkaLogService

router = APIRouter(prefix="/affiliate/api/v1/dashboard", tags=["02. Affiliate Performance Dashboard"])
log_service = KafkaLogService()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Global performance dashboard."""
    await log_service.log(None, "View_Admin_Dashboard", "Success", "Admin viewed global performance stats.")
    return await dashboard_service.get_summary(db)


@router.get("/my-stats", response_model=MyDashboardResponse)
async def my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_affiliate),
):
    """[Affiliate only] Personal analytics: clicks, conversions, earnings, platform and location breakdown."""
    profile_id_str = current_user.get("affiliate_profile_id")
    if not profile_id_str:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No affiliate profile linked to this account")
    await log_service.log(None, "View_My_Dashboard", "Success", f"Affiliate {current_user.get('username')} viewed personal stats.")
    return await dashboard_service.get_my_stats(db, uuid.UUID(profile_id_str))


@router.post("/simulate-sale")
async def simulate_sale(
    request: SimulateSaleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Inject a test conversion for dashboard demo/testing."""
    from app.models.conversion import Conversion
    from app.models.referral_link import ReferralLink
    from sqlalchemy import select
    result = await db.execute(select(ReferralLink).where(ReferralLink.generated_code == request.referral_code))
    link = result.scalar_one_or_none()
    if not link:
        return {"error": "Invalid referral code."}
    conversion = Conversion(
        affiliate_user_id=link.affiliate_profile_id,
        buyer_user_id=uuid.uuid4(),  # Simulated buyer
        product_id=request.product_id,
        sale_amount=request.sale_amount,
        commission_earned=request.sale_amount * 0.1,  # 10% demo commission
        referral_code=request.referral_code,
        customer_country="NG",
        referral_source="Simulated",
    )
    db.add(conversion)
    await db.commit()
    return {"message": "Sale simulated successfully. Refresh dashboard to see updates."}
