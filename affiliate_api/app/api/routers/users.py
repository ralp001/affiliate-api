# Source: AffiliateMarketing.API/Controllers/UserProvisioningController.cs
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.core.db import get_db
from app.core.security import create_access_token, require_support_admin
from app.schemas.identity import RegisterUserRequest, LoginRequest, TokenResponse
from app.models.user import User
from app.models.affiliate_profile import AffiliateProfile

router = APIRouter(prefix="/affiliate/api/v1/users", tags=["01. User Provisioning"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", status_code=201)
async def register_user(request: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    # Ensure unique username and email
    existing = (await db.execute(
        select(User).where((User.username == request.username) | (User.email == request.email))
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already registered")

    user = User(
        id=uuid.uuid4(),
        username=request.username,
        email=request.email,
        password_hash=pwd_context.hash(request.password),
        role=request.role,
        home_country=request.home_country,
    )
    db.add(user)

    affiliate_profile_id = None
    if request.role == "Affiliate":
        if not request.terms_accepted:
            raise HTTPException(status_code=400, detail="Affiliates must accept terms and conditions")
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
        "message": "User registered successfully",
        "user_id": str(user.id),
        "affiliate_profile_id": affiliate_profile_id,
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(
        select(User).where(User.username == request.username)
    )).scalar_one_or_none()

    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    affiliate_profile_id = None
    if user.role == "Affiliate":
        profile = (await db.execute(
            select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
        )).scalar_one_or_none()
        if profile:
            affiliate_profile_id = str(profile.id)

    token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "home_country": user.home_country,
        "affiliate_profile_id": affiliate_profile_id,
    })
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=str(user.id),
        affiliate_profile_id=affiliate_profile_id,
    )


@router.get("/", tags=["01. User Provisioning"])
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
