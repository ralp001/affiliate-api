import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product


async def create_product(db: AsyncSession, data: dict) -> Product:
    commission_type = data["commission_type"]
    commission_value = float(data["commission_value"])
    base_price = float(data["base_price"])

    if commission_type == "Percentage" and commission_value > 100:
        raise ValueError("Percentage commission cannot exceed 100%")
    if commission_type == "Fixed" and commission_value > base_price:
        raise ValueError("Fixed commission cannot exceed base price")

    product = Product(id=uuid.uuid4(), **data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def list_products(db: AsyncSession, available_only: bool = False) -> list[Product]:
    q = select(Product)
    if available_only:
        q = q.where(Product.is_available_for_affiliates == True)  # noqa: E712
    result = await db.execute(q.order_by(Product.name))
    return list(result.scalars().all())


async def toggle_availability(db: AsyncSession, product_id: uuid.UUID) -> Product | None:
    product = await db.get(Product, product_id)
    if not product:
        return None
    product.is_available_for_affiliates = not product.is_available_for_affiliates
    await db.commit()
    await db.refresh(product)
    return product


async def update_commission(
    db: AsyncSession,
    product_id: uuid.UUID,
    commission_type: str,
    commission_value: float,
) -> Product | None:
    product = await db.get(Product, product_id)
    if not product:
        return None
    if commission_type == "Fixed" and commission_value > float(product.base_price):
        raise ValueError("Fixed commission cannot exceed base price")
    if commission_type == "Percentage" and commission_value > 100:
        raise ValueError("Percentage commission cannot exceed 100%")
    product.commission_type = commission_type
    product.commission_value = commission_value
    await db.commit()
    await db.refresh(product)
    return product
