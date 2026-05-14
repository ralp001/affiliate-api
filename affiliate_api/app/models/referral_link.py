# Source: AffiliateMarketing.Domain/Entities/ReferralLink.cs
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base

class ReferralLink(Base):
    __tablename__ = "referral_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    affiliate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("affiliate_profiles.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    generated_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    source_platform: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
