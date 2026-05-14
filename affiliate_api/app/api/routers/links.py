# Source: AffiliateMarketing.API/Controllers/ReferralLinksController.cs
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.affiliate import GenerateLinkRequest, GenerateLinkResponse, ValidateReferralRequest, ValidationResultResponse
from app.services import affiliate_service, referral_service

router = APIRouter(prefix="/affiliate/api/v1/links", tags=["03. Referral Engine"])

@router.post("/generate", response_model=GenerateLinkResponse)
async def generate_link(request: GenerateLinkRequest, db: AsyncSession = Depends(get_db)):
    try:
        code = await affiliate_service.generate_link(db, uuid.uuid4(), request.product_id)
        return GenerateLinkResponse(referral_code=code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResultResponse)
async def validate_referral(request: ValidateReferralRequest, db: AsyncSession = Depends(get_db)):
    return await referral_service.validate_referral(
        db, request.referral_code, request.purchasing_user_id, request.product_id
    )
