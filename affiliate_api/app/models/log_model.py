import uuid
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped

from app.core.db import Base


class UserAction(str, enum.Enum):
    """Affiliate-API user action types for audit logging"""
    LOGIN = "Login"
    LOGOUT = "Logout"
    SIGNUP = "Signup"
    PROFILE_VIEW = "Profile View"
    PROFILE_UPDATE = "Profile Update"
    REFERRAL_LINK_CREATE = "Referral Link Create"
    REFERRAL_LINK_VIEW = "Referral Link View"
    CLICK_TRACK = "Click Track"
    CONVERSION_RECORD = "Conversion Record"
    RESOURCE_VIEW = "Resource View"
    RESOURCE_UPLOAD = "Resource Upload"
    ADMIN_ACTION = "Admin Action"


class ActionStatus(str, enum.Enum):
    SUCCESS = "Success"
    FAILED = "Failed"


class LogFailureReason(str, enum.Enum):
    INVALID_CREDENTIALS = "Invalid Credentials"
    ACCOUNT_LOCKED = "Account Locked"
    EMAIL_NOT_VERIFIED = "Email Not Verified"
    INVALID_OTP = "Invalid OTP"
    OTP_EXPIRED = "OTP Expired"
    WEAK_PASSWORD = "Weak Password"
    PASSWORD_MISMATCH = "Password Mismatch"
    EMAIL_ALREADY_EXISTS = "Email Already Exists"
    INVALID_INPUT = "Invalid Input"
    RATE_LIMIT_EXCEEDED = "Rate Limit Exceeded"
    NETWORK_ERROR = "Network Error"
    DATABASE_ERROR = "Database Error"
    KAFKA_ERROR = "Kafka Error"
    TOKEN_EXPIRED = "Token Expired"
    INSUFFICIENT_PERMISSIONS = "Insufficient Permissions"


class UserActionLog(Base):
    """Audit log for user actions — outbox pattern for reliable Kafka delivery"""
    __tablename__ = "logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True, index=True)
    responsibility_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    action: Mapped[UserAction] = mapped_column(
        Enum(UserAction, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    failure_reason: Mapped[Optional[LogFailureReason]] = mapped_column(
        Enum(LogFailureReason, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    synced_to_kafka: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def requires_retry(self) -> bool:
        return self.retry_count < 5 and not self.synced_to_kafka

    @property
    def next_retry_delay(self) -> int:
        return 2 ** self.retry_count
