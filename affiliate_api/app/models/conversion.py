# Source: AffiliateMarketing.Domain/Entities/Conversion.cs
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from app.core.db import Base

class Conversion(Base):
    __tablename__ = "conversions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    affiliate_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    buyer_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    sale_amount: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    commission_earned: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    referral_code: Mapped[str] = mapped_column(String, nullable=False)
    customer_country: Mapped[str | None] = mapped_column(String, nullable=True)
    referral_source: Mapped[str | None] = mapped_column(String, nullable=True)
    is_under_review: Mapped[bool] = mapped_column(Boolean, default=False)
    fraud_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
