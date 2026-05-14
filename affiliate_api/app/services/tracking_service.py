# Source: AffiliateMarketing.Application/Features/Tracking/Commands/RecordClickHandler.cs
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.referral_link import ReferralLink
from app.models.click_event import ClickEvent
from app.models.audit_log import AuditLog
from app.infrastructure.geolocation.ipinfo_service import IpInfoService

geo_service = IpInfoService()

# Velocity threshold: flag if same IP clicks same product more than N times per hour
CLICK_VELOCITY_THRESHOLD = 20


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
        platform=platform or "Organic",
        product_id=link.product_id,
        clicked_at=datetime.now(timezone.utc),
        country_code=geo.country_code,
        city=geo.city,
        region=geo.region,
        location=f"{geo.city}, {geo.country_code}",
    )
    db.add(click)

    # Velocity fraud check: if same IP has hit this product excessively this hour, log alert
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_clicks = (await db.execute(
        select(func.count()).select_from(ClickEvent).where(
            ClickEvent.ip_address == ip_address,
            ClickEvent.product_id == link.product_id,
            ClickEvent.clicked_at >= one_hour_ago,
        )
    )).scalar() or 0

    if recent_clicks >= CLICK_VELOCITY_THRESHOLD:
        db.add(AuditLog(
            entity_name="FraudAlert",
            action="High_Click_Velocity",
            new_values=f"IP {ip_address} clicked product {link.product_id} {recent_clicks + 1}x in last hour",
            performed_by="System",
        ))

    await db.commit()
    return f"https://emutare.com/products/{link.product_id}?ref={referral_code}"
