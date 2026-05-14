# Source: AffiliateMarketing.Application/Features/Affiliates/Commands/GenerateLinkHandler.cs
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.affiliate_profile import AffiliateProfile
from app.models.product import Product
from app.models.referral_link import ReferralLink
from datetime import datetime, timezone

async def generate_link(
    db: AsyncSession,
    affiliate_profile_id: uuid.UUID,
    product_id: uuid.UUID,
    source_platform: str = "Web",
) -> str:
    profile = await db.get(AffiliateProfile, affiliate_profile_id)
    product = await db.get(Product, product_id)

    if profile is None or product is None:
        raise ValueError("Invalid affiliate profile ID or product ID")

    # Preserve exact code format from GenerateLinkHandler.cs
    product_prefix = product.name[:3].upper()
    unique_suffix = str(uuid.uuid4())[:4]
    generated_code = f"{profile.tracking_id}-{product_prefix}-{unique_suffix}"

    link = ReferralLink(
        id=uuid.uuid4(),
        affiliate_profile_id=profile.id,
        product_id=product.id,
        generated_code=generated_code,
        source_platform=source_platform,
        created_at=datetime.now(timezone.utc),
    )
    db.add(link)
    await db.commit()
    return generated_code
