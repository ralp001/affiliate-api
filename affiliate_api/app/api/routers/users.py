# Source: AffiliateMarketing.API/Controllers/UserProvisioningController.cs
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.core.db import get_db
from app.schemas.identity import RegisterUserRequest
from app.models.user import User

router = APIRouter(prefix="/affiliate/api/v1/users", tags=["01. User Provisioning"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register_user(request: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    user = User(
        id=uuid.uuid4(),
        username=request.username,
        password_hash=pwd_context.hash(request.password),
        role=request.role,
        home_country=request.home_country,
    )
    db.add(user)
    await db.commit()
    return {"message": "User registered successfully", "user_id": str(user.id)}
