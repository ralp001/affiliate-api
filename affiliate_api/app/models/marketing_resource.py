import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped
from app.core.db import Base


class MarketingResource(Base):
    __tablename__ = "marketing_resources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String, nullable=False)  # Banner | Logo | Video
    title: Mapped[str] = mapped_column(String, nullable=False)
    asset_url: Mapped[str] = mapped_column(String, nullable=False)
    # HTML snippet with {tracking_id} and {product_id} placeholders for per-affiliate embedding
    html_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String, default="System")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
