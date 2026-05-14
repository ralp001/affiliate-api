# Source: AffiliateMarketing.Contracts/Identity/RegisterUserRequest.cs
from pydantic import BaseModel, field_validator


class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "Affiliate"  # Affiliate | SupportAdmin
    home_country: str = "Unknown"
    terms_accepted: bool = False

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        if v not in ("Affiliate", "SupportAdmin"):
            raise ValueError("Role must be Affiliate or SupportAdmin")
        return v

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v.strip() or "@" not in v:
            raise ValueError("A valid email is required")
        return v.strip().lower()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    affiliate_profile_id: str | None = None
