# Source: Affiliate.Events/AffiliateEvents.cs
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class SchemaDiscoveryEvent(BaseModel):
    api_name: str = "affiliate-marketing-api"
    tables: list = []
    hash: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AffiliateRegisteredEvent(BaseModel):
    affiliate_id: uuid.UUID
    business_name: str
    email: str
    region: str
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CommissionUpdatedEvent(BaseModel):
    affiliate_id: uuid.UUID
    new_rate: float
    currency: str = "NGN"
    updated_by: str
    effective_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserPermissionUpdatedEvent(BaseModel):
    user_id: uuid.UUID
    permissions: list[str]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
