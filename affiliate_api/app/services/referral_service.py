# Source: AffiliateMarketing.Application/Features/Referrals/Commands/ValidateReferralHandler.cs
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.referral_link import ReferralLink
from app.models.product import Product
from app.models.audit_log import AuditLog
from app.schemas.affiliate import ValidationResultResponse

async def validate_referral(
    db: AsyncSession,
    referral_code: str,
    purchasing_user_id: uuid.UUID,
    product_id: uuid.UUID,
) -> ValidationResultResponse:
    # 1. Fetch referral link with affiliate profile
    result = await db.execute(
        select(ReferralLink).where(ReferralLink.generated_code == referral_code)
    )
    link = result.scalar_one_or_none()

    if link is None or not link.is_active:
        return ValidationResultResponse(is_valid=False, message="Invalid or expired referral code.")

    # 2. Anti-fraud: block self-referral (ValidateReferralHandler.cs line 33)
    profile_result = await db.execute(
        select(ReferralLink).where(ReferralLink.id == link.id)
    )
    from app.models.affiliate_profile import AffiliateProfile
    profile = await db.get(AffiliateProfile, link.affiliate_profile_id)

    if profile and profile.user_id == purchasing_user_id:
        db.add(AuditLog(
            entity_name="Security_Alert",
            action="Self_Referral_Blocked",
            new_values=f"User: {purchasing_user_id} attempted to use code: {referral_code}",
            performed_by=str(purchasing_user_id),
        ))
        await db.commit()
        return ValidationResultResponse(
            is_valid=False,
            message="Fraud Alert: You cannot use your own referral link for discounts."
        )

    # 3. Calculate commission (ValidateReferralHandler.cs line 52-60)
    product = await db.get(Product, product_id)
    if product is None:
        return ValidationResultResponse(is_valid=False, message="Product not found.")

    commission = 0.0
    if product.commission_type == "Percentage":
        commission = (float(product.base_price) * float(product.commission_value)) / 100
    else:
        commission = float(product.commission_value)

    return ValidationResultResponse(
        is_valid=True,
        message="Referral validated successfully.",
        calculated_commission=commission,
    )
