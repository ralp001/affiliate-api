# Source: AffiliateMarketing.API/Controllers/ClickTrackingController.cs
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services import tracking_service

router = APIRouter(prefix="/api/v1/r", tags=["04. Public Tracking"])

@router.get("/{code}")
async def redirect_and_track(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    # Preserve proxy-aware IP extraction (ClickTrackingController.cs line 22-25)
    ip_address = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "Unknown")
    )
    user_agent = request.headers.get("user-agent", "")
    platform = request.query_params.get("utm_source") or "Organic"

    target_url = await tracking_service.record_click(db, code, ip_address, user_agent, platform)

    # Boss requirement: never show 404 (ClickTrackingController.cs line 44-46)
    return RedirectResponse(target_url or "https://emutare.com")
