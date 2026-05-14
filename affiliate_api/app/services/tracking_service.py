# Source: AffiliateMarketing.Application/Features/Tracking/Commands/RecordClickHandler.cs
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.referral_link import ReferralLink
from app.models.click_event import ClickEvent
from app.infrastructure.geolocation.ipinfo_service import IpInfoService

geo_service = IpInfoService()

async def record_click(
    db: AsyncSession,
    referral_code: str,
    ip_address: str,
    user_agent: str,
    platform: str,
) -> str:
    result = await db.execute(
        select(ReferralLink).where(ReferralLink.generated_code == referral_code)
    )
    link = result.scalar_one_or_none()

    if link is None:
        return "https://emutare.com/404"

    geo = await geo_service.get_location(ip_address)

    click = ClickEvent(
        id=uuid.uuid4(),
        tracking_id=referral_code,
        ip_address=ip_address,
        user_agent=user_agent or "Unknown",
        platform=platform or "Direct",
        product_id=link.product_id,
        clicked_at=datetime.now(timezone.utc),
        country_code=geo.country_code,
        city=geo.city,
        region=geo.region,
        location=f"{geo.city}, {geo.country_code}",
    )
    db.add(click)
    await db.commit()

    return f"https://emutare.com/products/{link.product_id}?ref={referral_code}"
