import uuid
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.db import get_db

bearer_scheme = HTTPBearer(auto_error=False)

# Maps issuer → signing secret
_JWT_SECRETS = {
    "internal-auth-api": settings.INTERNAL_AUTH_JWT_SECRET,
    "external-auth-api": settings.EXTERNAL_AUTH_JWT_SECRET,
}


def create_access_token(data: dict, issuer: str = "external-auth-api") -> str:
    """Issue a local dev/test token using the correct issuer secret."""
    secret = _JWT_SECRETS.get(issuer, settings.INTERNAL_AUTH_JWT_SECRET)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {**data, "iss": issuer, "type": "access", "exp": expire}
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Multi-tenant JWT authentication.
    Accepts tokens from both internal-auth-api (staff) and external-auth-api (affiliates).
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Step 1: unverified decode to read issuer
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except JWTError:
        raise cred_exc

    issuer = unverified.get("iss")
    secret = _JWT_SECRETS.get(issuer)
    if not secret:
        raise cred_exc

    # Step 2: verified decode with issuer-specific secret
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise cred_exc

    # Step 3: validate token type
    if payload.get("type") != "access":
        raise cred_exc

    user_id: str = payload.get("sub")
    if not user_id:
        raise cred_exc

    # Step 4: build user context based on issuer
    if issuer == "internal-auth-api":
        return {
            "id": user_id,
            "email": payload.get("email", ""),
            "responsibility_category": payload.get("responsibility_category", ""),
            "role": "SupportAdmin",
            "issuer": issuer,
            "affiliate_profile_id": None,
        }

    # external-auth-api — look up affiliate profile
    from app.models.affiliate_profile import AffiliateProfile
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise cred_exc

    profile = (await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == uid)
    )).scalar_one_or_none()

    return {
        "id": user_id,
        "email": payload.get("email", ""),
        "responsibility_category": payload.get("responsibility_category", "affiliate"),
        "role": "Affiliate",
        "issuer": issuer,
        "affiliate_profile_id": str(profile.id) if profile else None,
    }


def require_role(*roles: str):
    """Returns a FastAPI dependency that enforces one of the given roles."""
    async def _checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _checker


require_affiliate = require_role("Affiliate")
require_support_admin = require_role("SupportAdmin")
