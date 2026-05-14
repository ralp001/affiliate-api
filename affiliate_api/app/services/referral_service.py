# Source: AffiliateMarketing.Application/Features/Referrals/Commands/ValidateReferralHandler.cs
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.referral_link import ReferralLink
from app.models.product import Product
from app.models.audit_log import AuditLog
from app.models.conversion import Conversion
from app.models.click_event import ClickEvent
from app.schemas.affiliate import ValidationResultResponse


async def validate_referral(
    db: AsyncSession,
    referral_code: str,
    purchasing_user_id: uuid.UUID,
    product_id: uuid.UUID,
) -> ValidationResultResponse:
    # 1. Fetch referral link
    result = await db.execute(
        select(ReferralLink).where(ReferralLink.generated_code == referral_code)
    )
    link = result.scalar_one_or_none()

    if link is None or not link.is_active:
        return ValidationResultResponse(is_valid=False, message="Invalid or expired referral code.")

    # 2. Anti-fraud: block self-referral
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

    # 3. Calculate commission
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


async def record_conversion(
    db: AsyncSession,
    referral_code: str,
    purchasing_user_id: uuid.UUID,
    product_id: uuid.UUID,
    sale_amount: float,
    customer_country: str | None = None,
) -> Conversion:
    """Record an attributed conversion, applying fraud heuristics."""
    result = await db.execute(
        select(ReferralLink).where(ReferralLink.generated_code == referral_code)
    )
    link = result.scalar_one_or_none()
    if link is None or not link.is_active:
        raise ValueError("Invalid or inactive referral code.")

    product = await db.get(Product, product_id)
    if product is None:
        raise ValueError("Product not found.")

    # Calculate commission
    commission = 0.0
    if product.commission_type == "Percentage":
        commission = (sale_amount * float(product.commission_value)) / 100
    else:
        commission = float(product.commission_value)

    # Fraud checks
    is_under_review = False
    fraud_reason = None

    from app.models.affiliate_profile import AffiliateProfile
    profile = await db.get(AffiliateProfile, link.affiliate_profile_id)

    # Check 1: Self-referral
    if profile and profile.user_id == purchasing_user_id:
        is_under_review = True
        fraud_reason = "Self-referral detected"

    # Check 2: Suspicious velocity — same buyer with multiple referral conversions in 24h
    if not is_under_review:
        recent_count = (await db.execute(
            select(func.count()).select_from(Conversion).where(
                Conversion.buyer_user_id == purchasing_user_id,
                Conversion.processed_at >= datetime.now(timezone.utc) - timedelta(hours=24),
            )
        )).scalar() or 0
        if recent_count >= 3:
            is_under_review = True
            fraud_reason = f"Suspicious: {recent_count + 1} conversions from same buyer in 24h"

    conversion = Conversion(
        id=uuid.uuid4(),
        affiliate_user_id=link.affiliate_profile_id,
        buyer_user_id=purchasing_user_id,
        product_id=product_id,
        sale_amount=sale_amount,
        commission_earned=0.0 if is_under_review else commission,
        referral_code=referral_code,
        customer_country=customer_country,
        referral_source=link.source_platform,
        is_under_review=is_under_review,
        fraud_reason=fraud_reason,
    )
    db.add(conversion)

    db.add(AuditLog(
        entity_name="Conversion",
        action="Conversion_Recorded" if not is_under_review else "Conversion_Flagged",
        new_values=f"code={referral_code} amount={sale_amount} commission={conversion.commission_earned}",
        performed_by=str(purchasing_user_id),
    ))
    await db.commit()
    await db.refresh(conversion)
    return conversion
