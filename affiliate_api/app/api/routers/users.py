# Source: AffiliateMarketing.API/Controllers/UserProvisioningController.cs
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.core.db import get_db
from app.core.security import create_access_token, require_support_admin
from app.schemas.identity import RegisterUserRequest, LoginRequest, TokenResponse
from app.schemas.common import RegisterResponse, UserItem
from app.models.user import User
from app.models.affiliate_profile import AffiliateProfile
from app.decorators.log_user_action import log_user_action
from app.models.log_model import UserAction
from app.i18n import t, DEFAULT_LANGUAGE

router = APIRouter(prefix="/api/v1/users", tags=["01. User Provisioning"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", status_code=201, response_model=RegisterResponse)
@log_user_action(action=UserAction.SIGNUP)
async def register_user(req: Request, body: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    lang = getattr(req.state, "language", DEFAULT_LANGUAGE)
    # Ensure unique username and email
    existing = (await db.execute(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail=t("registration.username_or_email_taken", lang))

    user = User(
        id=uuid.uuid4(),
        username=body.username,
        email=body.email,
        password_hash=pwd_context.hash(body.password),
        role=body.role,
        home_country=body.home_country,
    )
    db.add(user)

    affiliate_profile_id = None
    if body.role == "Affiliate":
        if not body.terms_accepted:
            raise HTTPException(status_code=400, detail=t("registration.terms_required", lang))
        await db.flush()  # flush user so FK constraint is satisfied when profile is inserted
        tracking_id = f"AFF-{str(uuid.uuid4())[:8].upper()}"
        profile = AffiliateProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            tracking_id=tracking_id,
            terms_accepted=True,
        )
        db.add(profile)
        affiliate_profile_id = str(profile.id)

    await db.commit()
    return {
        "message": t("registration.signup_successful", lang),
        "user_id": str(user.id),
        "affiliate_profile_id": affiliate_profile_id,
    }


@router.post("/login", response_model=TokenResponse)
@log_user_action(action=UserAction.LOGIN)
async def login(req: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    lang = getattr(req.state, "language", DEFAULT_LANGUAGE)
    user = (await db.execute(
        select(User).where(User.username == body.username)
    )).scalar_one_or_none()

    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail=t("auth.invalid_credentials", lang))

    affiliate_profile_id = None
    if user.role == "Affiliate":
        profile = (await db.execute(
            select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
        )).scalar_one_or_none()
        if profile:
            affiliate_profile_id = str(profile.id)

    # Issue token with correct issuer so multi-tenant auth can validate it
    issuer = "internal-auth-api" if user.role == "SupportAdmin" else "external-auth-api"
    token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "responsibility_category": user.role.lower(),
        "home_country": user.home_country,
    }, issuer=issuer)
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=str(user.id),
        affiliate_profile_id=affiliate_profile_id,
    )


@router.get("/", response_model=list[UserItem], tags=["01. User Provisioning"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] List all registered users."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "home_country": u.home_country,
            "created_at": u.created_at.isoformat(),
            "is_verified": u.is_verified,
        }
        for u in users
    ]
