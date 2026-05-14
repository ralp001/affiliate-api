# Source: AffiliateMarketing.Contracts/Products/CreateProductRequest.cs
import uuid
from pydantic import BaseModel, field_validator

class CreateProductRequest(BaseModel):
    name: str
    description: str
    product_type: str = "Individual"
    subscription_plan: str = "Starter"
    commission_type: str  # Percentage or Fixed
    commission_value: float
    base_price: float
    currency: str = "NGN"

    @field_validator("commission_type")
    @classmethod
    def validate_commission_type(cls, v: str) -> str:
        if v not in ("Percentage", "Fixed"):
            raise ValueError("commission_type must be Percentage or Fixed")
        return v

class SetCommissionRequest(BaseModel):
    product_id: uuid.UUID
    commission_type: str
    commission_value: float
