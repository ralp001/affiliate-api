# Source: AffiliateMarketing.API/Controllers/AdminManagementController.cs
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import require_support_admin
from app.models.audit_log import AuditLog
from app.models.conversion import Conversion
from app.models.marketing_resource import MarketingResource
from app.models.affiliate_profile import AffiliateProfile
from app.models.user import User
from app.services import product_service
from app.schemas.products import (
    CreateProductRequest, SetCommissionRequest, ProductResponse,
    CreateResourceRequest, ResourceResponse, FraudConversionResponse,
)
from app.schemas.common import (
    AffiliateItem, AuditLogItem, ResourceCreatedResponse,
    FraudApprovedResponse, MessageResponse,
)
from app.infrastructure.kafka.log_service import KafkaLogService

router = APIRouter(prefix="/api/v1/admin", tags=["05. System Administration"])
log_service = KafkaLogService()


# ─── Products ─────────────────────────────────────────────────────────────────

@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    request: CreateProductRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Create an affiliate-visible product offering."""
    try:
        product = await product_service.create_product(db, request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await log_service.log(None, "Create_Product", "Success", f"Product '{product.name}' created by {current_user.get('username')}")
    return product


@router.get("/products", response_model=list[ProductResponse])
async def list_all_products(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] List all products (including unavailable ones)."""
    return await product_service.list_products(db, available_only=False)


@router.put("/products/{product_id}/commission", response_model=ProductResponse)
async def update_product_commission(
    product_id: uuid.UUID,
    request: SetCommissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Update commission type and value for a product."""
    try:
        product = await product_service.update_commission(
            db, product_id, request.commission_type, request.commission_value
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await log_service.log(None, "Update_Commission", "Success", f"Product {product_id} commission updated by {current_user.get('username')}")
    return product


@router.put("/products/{product_id}/toggle-availability", response_model=ProductResponse)
async def toggle_product_availability(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Toggle whether a product is visible to affiliates."""
    product = await product_service.toggle_availability(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await log_service.log(None, "Toggle_Product_Availability", "Success", f"Product {product_id} availability toggled by {current_user.get('username')}")
    return product


# ─── Marketing Resources ──────────────────────────────────────────────────────

@router.post("/resources", status_code=201, response_model=ResourceCreatedResponse)
async def create_resource(
    request: CreateResourceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Add a marketing resource (banner/logo/video) for a product."""
    resource = MarketingResource(
        id=uuid.uuid4(),
        product_id=request.product_id,
        resource_type=request.resource_type,
        title=request.title,
        asset_url=request.asset_url,
        html_template=request.html_template,
        created_by=current_user.get("username", "admin"),
    )
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return {"id": str(resource.id), "message": "Resource created successfully"}


# ─── Fraud Review ─────────────────────────────────────────────────────────────

@router.get("/fraud-review", response_model=list[FraudConversionResponse])
async def list_fraud_reviews(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] List all conversions flagged for fraud review."""
    result = await db.execute(
        select(Conversion)
        .where(Conversion.is_under_review == True)  # noqa: E712
        .order_by(Conversion.processed_at.desc())
    )
    return result.scalars().all()


@router.put("/fraud-review/{conversion_id}/approve", response_model=FraudApprovedResponse)
async def approve_conversion(
    conversion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Approve a flagged conversion and credit the affiliate commission."""
    from app.models.product import Product
    conversion = await db.get(Conversion, conversion_id)
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    if not conversion.is_under_review:
        raise HTTPException(status_code=400, detail="Conversion is not under review")

    # Recalculate and credit commission
    product = await db.get(Product, conversion.product_id)
    if product:
        if product.commission_type == "Percentage":
            conversion.commission_earned = (float(conversion.sale_amount) * float(product.commission_value)) / 100
        else:
            conversion.commission_earned = float(product.commission_value)

    conversion.is_under_review = False
    conversion.fraud_reason = None
    await db.commit()
    await log_service.log(None, "Fraud_Approved", "Success", f"Conversion {conversion_id} approved by {current_user.get('username')}")
    return {"message": "Conversion approved and commission credited", "commission_earned": float(conversion.commission_earned)}


@router.put("/fraud-review/{conversion_id}/reject", response_model=MessageResponse)
async def reject_conversion(
    conversion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Reject a flagged conversion (commission stays at 0)."""
    conversion = await db.get(Conversion, conversion_id)
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    conversion.is_under_review = False
    conversion.fraud_reason = f"Rejected by {current_user.get('username')}"
    conversion.commission_earned = 0
    await db.commit()
    await log_service.log(None, "Fraud_Rejected", "Success", f"Conversion {conversion_id} rejected by {current_user.get('username')}")
    return {"message": "Conversion rejected"}


# ─── Affiliates List ──────────────────────────────────────────────────────────

@router.get("/affiliates", response_model=list[AffiliateItem])
async def list_affiliates(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] List all active affiliates with their tracking IDs and join date."""
    result = await db.execute(
        select(AffiliateProfile, User)
        .join(User, User.id == AffiliateProfile.user_id)
        .order_by(AffiliateProfile.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "affiliate_profile_id": str(profile.id),
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "tracking_id": profile.tracking_id,
            "home_country": user.home_country,
            "is_active": profile.is_active,
            "joined_at": profile.created_at.isoformat(),
        }
        for profile, user in rows
    ]


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs/{entity_name}", response_model=list[AuditLogItem])
async def get_audit_logs(
    entity_name: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_support_admin),
):
    """[SupportAdmin only] Retrieve audit log entries for a given entity type."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_name == entity_name)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "entity_name": log.entity_name,
            "action": log.action,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "performed_by": log.performed_by,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
