from pydantic import BaseModel


# -- User / Auth ---------------------------------------------------------------

class RegisterResponse(BaseModel):
    message: str
    user_id: str
    affiliate_profile_id: str | None = None


class UserItem(BaseModel):
    id: str
    username: str
    email: str
    role: str
    home_country: str
    created_at: str
    is_verified: bool


# -- Referral Links ------------------------------------------------------------

class ReferralLinkItem(BaseModel):
    referral_code: str
    tracking_url: str
    product_id: str
    source_platform: str
    is_active: bool
    created_at: str


class ConversionRecordedResponse(BaseModel):
    id: str
    commission_earned: float
    is_under_review: bool
    message: str


# -- Admin ---------------------------------------------------------------------

class AffiliateItem(BaseModel):
    affiliate_profile_id: str
    user_id: str
    username: str
    email: str
    tracking_id: str
    home_country: str
    is_active: bool
    joined_at: str


class AuditLogItem(BaseModel):
    id: str
    entity_name: str
    action: str
    old_values: str | None
    new_values: str | None
    performed_by: str | None
    created_at: str


class ResourceCreatedResponse(BaseModel):
    id: str
    message: str


class FraudApprovedResponse(BaseModel):
    message: str
    commission_earned: float


class MessageResponse(BaseModel):
    message: str
