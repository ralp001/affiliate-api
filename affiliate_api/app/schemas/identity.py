# Source: AffiliateMarketing.Contracts/Identity/RegisterUserRequest.cs
from pydantic import BaseModel, field_validator

class RegisterUserRequest(BaseModel):
    username: str
    password: str
    role: str = "Affiliate"
    home_country: str = "Unknown"

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
