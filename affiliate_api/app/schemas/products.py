# Source: AffiliateMarketing.Contracts/Products/CreateProductRequest.cs
import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator


class CreateProductRequest(BaseModel):
    name: str
    description: str
    product_type: str = "Individual"  # Individual | Business | Enterprise
    subscription_plan: str = "Starter"  # Free-form plan name, e.g. Platinum, Gold, Small
    commission_type: str  # Percentage | Fixed
    commission_value: float
    base_price: float
    currency: str = "NGN"

    @field_validator("commission_type")
    @classmethod
    def validate_commission_type(cls, v: str) -> str:
        if v not in ("Percentage", "Fixed"):
            raise ValueError("commission_type must be Percentage or Fixed")
        return v

    @field_validator("base_price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("commission_value")
    @classmethod
    def commission_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Commission cannot be negative")
        return v


class SetCommissionRequest(BaseModel):
    commission_type: str
    commission_value: float

    @field_validator("commission_type")
    @classmethod
    def validate_commission_type(cls, v: str) -> str:
        if v not in ("Percentage", "Fixed"):
            raise ValueError("commission_type must be Percentage or Fixed")
        return v


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    product_type: str
    subscription_plan: str
    commission_type: str
    commission_value: float
    base_price: float
    currency: str
    is_available_for_affiliates: bool

    class Config:
        from_attributes = True


class CreateResourceRequest(BaseModel):
    product_id: uuid.UUID
    resource_type: str  # Banner | Logo | Video
    title: str
    asset_url: str
    html_template: str | None = None


class ResourceResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    resource_type: str
    title: str
    asset_url: str
    html_snippet: str | None = None  # Template with affiliate tracking ID already embedded
    created_at: datetime

    class Config:
        from_attributes = True


class FraudConversionResponse(BaseModel):
    id: uuid.UUID
    referral_code: str
    sale_amount: float
    commission_earned: float
    customer_country: str | None
    fraud_reason: str | None
    processed_at: datetime

    class Config:
        from_attributes = True
