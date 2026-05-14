# Source: AffiliateMarketing.Contracts/Affiliate/*
import uuid
from pydantic import BaseModel

class GenerateLinkRequest(BaseModel):
    product_id: uuid.UUID

class GenerateLinkResponse(BaseModel):
    referral_code: str

class ValidateReferralRequest(BaseModel):
    referral_code: str
    purchasing_user_id: uuid.UUID
    product_id: uuid.UUID

class ValidationResultResponse(BaseModel):
    is_valid: bool
    message: str
    calculated_commission: float = 0.0

class SimulateSaleRequest(BaseModel):
    referral_code: str
    product_id: uuid.UUID
    sale_amount: float
