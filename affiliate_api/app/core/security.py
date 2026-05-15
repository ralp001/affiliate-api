import uuid
from typing import Dict, Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.db import get_db
from app.i18n import t, is_supported, normalize, DEFAULT_LANGUAGE

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
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Multi-tenant JWT authentication.
    Accepts tokens from both internal-auth-api (staff) and external-auth-api (affiliates).
    When DISABLE_AUTH=true in .env every request is treated as a SupportAdmin (demo only).
    """
    lang = getattr(request.state, "language", DEFAULT_LANGUAGE)

    # ── Auth bypass (demo / smoke-test mode) ──────────────────────────────────
    if settings.DISABLE_AUTH:
        # Try to pick up a real affiliate profile so affiliate-only endpoints work too
        from app.models.affiliate_profile import AffiliateProfile as _AP
        _profile = (await db.execute(select(_AP).limit(1))).scalar_one_or_none()
        return {
            "id": str(_profile.user_id) if _profile else "00000000-0000-0000-0000-000000000000",
            "username": "demo",
            "email": "demo@emutare.io",
            "responsibility_category": "SupportAdmin",
            "role": "SupportAdmin",
            "issuer": "demo",
            "affiliate_profile_id": str(_profile.id) if _profile else None,
        }

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("auth.not_authenticated", lang))

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=t("auth.could_not_validate_credentials", lang),
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Step 1: unverified decode to read issuer
    # python-jose requires key="" even when verify_signature=False
    try:
        unverified = jwt.decode(token, key="", options={"verify_signature": False})
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

    # Step 4: refine language from JWT preferred_language claim (skip if explicit override)
    if not request.headers.get("X-Language") and not request.query_params.get("lang"):
        jwt_lang = payload.get("preferred_language", "")
        if jwt_lang and is_supported(jwt_lang):
            request.state.language = normalize(jwt_lang)
            lang = request.state.language

    # Step 5: build user context based on issuer
    if issuer == "internal-auth-api":
        return {
            "id": user_id,
            "username": payload.get("username", ""),
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
        "username": payload.get("username", ""),
        "email": payload.get("email", ""),
        "responsibility_category": payload.get("responsibility_category", "affiliate"),
        "role": "Affiliate",
        "issuer": issuer,
        "affiliate_profile_id": str(profile.id) if profile else None,
    }


def require_role(*roles: str):
    """Returns a FastAPI dependency that enforces one of the given roles."""
    async def _checker(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        # When DISABLE_AUTH=true all role checks are bypassed for demo/testing
        if settings.DISABLE_AUTH:
            return user
        if user.get("role") not in roles:
            lang = getattr(request.state, "language", DEFAULT_LANGUAGE)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("auth.insufficient_permissions", lang))
        return user
    return _checker


require_affiliate = require_role("Affiliate")
require_support_admin = require_role("SupportAdmin")
