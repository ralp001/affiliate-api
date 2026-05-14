# Source: AffiliateMarketing.Application/Features/Dashboard/Handlers/GetDashboardSummaryHandler.cs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.conversion import Conversion
from app.models.click_event import ClickEvent
from app.models.product import Product
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.models.affiliate_profile import AffiliateProfile
from app.schemas.dashboard import (
    DashboardSummaryResponse, AffiliatePerformanceSchema,
    CountryProductMetricSchema, CountryMetricSchema,
)

async def get_summary(db: AsyncSession) -> DashboardSummaryResponse:
    # 1. Top product by sales
    top_product_row = (await db.execute(
        select(Conversion.product_id, func.sum(Conversion.sale_amount).label("total"))
        .group_by(Conversion.product_id)
        .order_by(func.sum(Conversion.sale_amount).desc())
        .limit(1)
    )).first()

    product_name = "No Sales Yet"
    if top_product_row:
        p = await db.get(Product, top_product_row.product_id)
        product_name = p.name if p else "Unknown Product"

    # 2. Top country by visits
    top_visit = (await db.execute(
        select(ClickEvent.country_code, func.count().label("cnt"))
        .where(ClickEvent.country_code.isnot(None))
        .group_by(ClickEvent.country_code)
        .order_by(func.count().desc())
        .limit(1)
    )).first()
    top_visit_country = top_visit.country_code if top_visit else "N/A"

    # 3. Top country by purchases
    top_purchase = (await db.execute(
        select(Conversion.customer_country, func.count().label("cnt"))
        .where(Conversion.customer_country.isnot(None))
        .group_by(Conversion.customer_country)
        .order_by(func.count().desc())
        .limit(1)
    )).first()
    top_purchase_country = top_purchase.customer_country if top_purchase else "N/A"

    # 4. Total revenue
    total_rev_row = (await db.execute(select(func.sum(Conversion.sale_amount)))).scalar()
    total_revenue = float(total_rev_row or 0)

    # 5. Total clicks
    total_clicks = (await db.execute(select(func.count()).select_from(ClickEvent))).scalar() or 0

    # 6. Top 5 affiliates by sales
    top_sales_rows = (await db.execute(
        select(Conversion.affiliate_user_id, func.count().label("sales"), func.sum(Conversion.sale_amount).label("rev"))
        .group_by(Conversion.affiliate_user_id)
        .order_by(func.count().desc())
        .limit(5)
    )).all()

    top_affiliates_by_sales = []
    for row in top_sales_rows:
        user = (await db.execute(select(User).where(User.id == row.affiliate_user_id))).scalar_one_or_none()
        if user:
            top_affiliates_by_sales.append(AffiliatePerformanceSchema(
                username=user.username, home_country=user.home_country,
                created_at=user.created_at, count=row.sales, revenue=float(row.rev or 0)
            ))

    # 7. Top 5 affiliates by click links
    top_link_rows = (await db.execute(
        select(ReferralLink.affiliate_profile_id, func.count().label("clicks"))
        .join(ClickEvent, ClickEvent.tracking_id == ReferralLink.generated_code)
        .group_by(ReferralLink.affiliate_profile_id)
        .order_by(func.count().desc())
        .limit(5)
    )).all()

    top_affiliates_by_links = []
    for row in top_link_rows:
        profile = await db.get(AffiliateProfile, row.affiliate_profile_id)
        if profile:
            user = (await db.execute(select(User).where(User.id == profile.user_id))).scalar_one_or_none()
            if user:
                top_affiliates_by_links.append(AffiliatePerformanceSchema(
                    username=user.username, home_country=user.home_country,
                    created_at=user.created_at, count=row.clicks
                ))

    # 8. Top 5 country+product metrics
    country_product_rows = (await db.execute(
        select(Conversion.customer_country, Conversion.product_id, func.count().label("cnt"))
        .group_by(Conversion.customer_country, Conversion.product_id)
        .order_by(func.count().desc())
        .limit(5)
    )).all()

    top_countries_with_products = []
    for row in country_product_rows:
        p = await db.get(Product, row.product_id)
        top_countries_with_products.append(CountryProductMetricSchema(
            country=row.customer_country or "Unknown",
            product_name=p.name if p else "Unknown Product",
            count=row.cnt,
        ))

    # 9. Geographic breakdown
    geo_rows = (await db.execute(
        select(ClickEvent.country_code, func.count().label("cnt"))
        .where(ClickEvent.country_code.isnot(None))
        .group_by(ClickEvent.country_code)
    )).all()

    geographic_breakdown = [
        CountryMetricSchema(country_code=row.country_code, click_count=row.cnt)
        for row in geo_rows
    ]

    return DashboardSummaryResponse(
        top_product_by_sales=product_name,
        total_revenue=total_revenue,
        top_country_by_visits=top_visit_country,
        top_country_by_purchases=top_purchase_country,
        total_clicks=total_clicks,
        top_affiliates_by_sales=top_affiliates_by_sales,
        top_affiliates_by_links=top_affiliates_by_links,
        top_countries_with_products=top_countries_with_products,
        geographic_breakdown=geographic_breakdown,
    )
