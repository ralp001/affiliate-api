# Marketing resources with embedded affiliate attribution
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.config import settings
from app.core.security import require_affiliate
from app.models.marketing_resource import MarketingResource

router = APIRouter(prefix="/affiliate/api/v1/resources", tags=["07. Marketing Resources"])


@router.get("/")
async def list_resources(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_affiliate),
):
    """[Affiliate only] Get all marketing resources with tracking ID already embedded in HTML snippets."""
    tracking_id = current_user.get("affiliate_profile_id", "UNKNOWN")
    base_url = settings.APP_BASE_URL

    result = await db.execute(
        select(MarketingResource).order_by(MarketingResource.created_at.desc())
    )
    resources = result.scalars().all()

    return [
        _build_resource_response(r, tracking_id, base_url)
        for r in resources
    ]


@router.get("/by-product/{product_id}")
async def list_resources_for_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_affiliate),
):
    """[Affiliate only] Get marketing resources for a specific product, with tracking pre-embedded."""
    tracking_id = current_user.get("affiliate_profile_id", "UNKNOWN")
    base_url = settings.APP_BASE_URL

    result = await db.execute(
        select(MarketingResource)
        .where(MarketingResource.product_id == product_id)
        .order_by(MarketingResource.resource_type)
    )
    resources = result.scalars().all()

    return [
        _build_resource_response(r, tracking_id, base_url)
        for r in resources
    ]


def _build_resource_response(resource: MarketingResource, tracking_id: str, base_url: str) -> dict:
    """Embed the affiliate's tracking ID into the HTML snippet template."""
    html_snippet = None
    if resource.html_template:
        html_snippet = (
            resource.html_template
            .replace("{tracking_id}", str(tracking_id))
            .replace("{product_id}", str(resource.product_id))
            .replace("{base_url}", base_url)
        )

    return {
        "id": str(resource.id),
        "product_id": str(resource.product_id),
        "resource_type": resource.resource_type,
        "title": resource.title,
        "asset_url": resource.asset_url,
        "html_snippet": html_snippet,
        "created_at": resource.created_at.isoformat(),
    }
