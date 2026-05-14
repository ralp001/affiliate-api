# Affiliate-facing product catalog
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import require_affiliate
from app.services import product_service
from app.schemas.products import ProductResponse

router = APIRouter(prefix="/affiliate/api/v1/products", tags=["06. Product Catalog"])


@router.get("/", response_model=list[ProductResponse])
async def list_available_products(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_affiliate),
):
    """[Affiliate only] Browse all products available for promotion."""
    return await product_service.list_products(db, available_only=True)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_affiliate),
):
    """[Affiliate only] Get details for a specific product including commission rate."""
    from app.models.product import Product
    product = await db.get(Product, product_id)
    if not product or not product.is_available_for_affiliates:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found or unavailable")
    return product
