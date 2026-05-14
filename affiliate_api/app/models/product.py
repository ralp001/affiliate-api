# Source: AffiliateMarketing.Domain/Entities/Product.cs
import uuid
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import mapped_column, Mapped
from app.core.db import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    product_type: Mapped[str] = mapped_column(String, default="Individual")
    subscription_plan: Mapped[str] = mapped_column(String, default="Starter")
    commission_type: Mapped[str] = mapped_column(String, nullable=False)  # Percentage or Fixed
    commission_value: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    base_price: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    currency: Mapped[str] = mapped_column(String, default="NGN")
    is_available_for_affiliates: Mapped[bool] = mapped_column(Boolean, default=True)
