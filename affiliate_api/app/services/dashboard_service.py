# Source: AffiliateMarketing.Application/Features/Dashboard/Handlers/GetDashboardSummaryHandler.cs
import uuid
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
    MyDashboardResponse, AffiliatePlatformMetric,
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


async def get_my_stats(db: AsyncSession, affiliate_profile_id: uuid.UUID) -> MyDashboardResponse:
    """Personal analytics dashboard for an authenticated affiliate."""
    links_result = await db.execute(
        select(ReferralLink.generated_code, ReferralLink.product_id)
        .where(ReferralLink.affiliate_profile_id == affiliate_profile_id)
    )
    links = links_result.all()
    codes = [lnk.generated_code for lnk in links]

    if not codes:
        return MyDashboardResponse(
            total_clicks=0, total_conversions=0, confirmed_earnings=0.0,
            pending_earnings=0.0, top_product=None,
            platform_breakdown=[], location_breakdown=[],
        )

    # Total clicks
    total_clicks = (await db.execute(
        select(func.count()).select_from(ClickEvent)
        .where(ClickEvent.tracking_id.in_(codes))
    )).scalar() or 0

    # Confirmed conversions
    confirmed_rows = (await db.execute(
        select(Conversion)
        .where(Conversion.referral_code.in_(codes), Conversion.is_under_review == False)  # noqa: E712
    )).scalars().all()
    total_conversions = len(confirmed_rows)
    confirmed_earnings = sum(float(c.commission_earned) for c in confirmed_rows)

    # Pending earnings (under fraud review)
    pending_earnings = float((await db.execute(
        select(func.sum(Conversion.commission_earned))
        .where(Conversion.referral_code.in_(codes), Conversion.is_under_review == True)  # noqa: E712
    )).scalar() or 0)

    # Top product
    top_product_name = None
    top_product_row = (await db.execute(
        select(Conversion.product_id, func.sum(Conversion.sale_amount).label("total"))
        .where(Conversion.referral_code.in_(codes), Conversion.is_under_review == False)  # noqa: E712
        .group_by(Conversion.product_id)
        .order_by(func.sum(Conversion.sale_amount).desc())
        .limit(1)
    )).first()
    if top_product_row:
        p = await db.get(Product, top_product_row.product_id)
        top_product_name = p.name if p else "Unknown"

    # Platform breakdown
    platform_rows = (await db.execute(
        select(ClickEvent.platform, func.count().label("cnt"))
        .where(ClickEvent.tracking_id.in_(codes))
        .group_by(ClickEvent.platform)
    )).all()

    platform_breakdown = []
    for row in platform_rows:
        conv_count = (await db.execute(
            select(func.count()).select_from(Conversion).where(
                Conversion.referral_code.in_(codes),
                Conversion.referral_source == row.platform,
                Conversion.is_under_review == False,  # noqa: E712
            )
        )).scalar() or 0
        platform_breakdown.append(AffiliatePlatformMetric(
            platform=row.platform or "Organic",
            clicks=row.cnt,
            conversions=conv_count,
        ))

    # Location breakdown (top 10 countries by clicks)
    geo_rows = (await db.execute(
        select(ClickEvent.country_code, func.count().label("cnt"))
        .where(ClickEvent.tracking_id.in_(codes), ClickEvent.country_code.isnot(None))
        .group_by(ClickEvent.country_code)
        .order_by(func.count().desc())
        .limit(10)
    )).all()

    location_breakdown = [
        CountryMetricSchema(country_code=r.country_code, click_count=r.cnt)
        for r in geo_rows
    ]

    return MyDashboardResponse(
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        confirmed_earnings=confirmed_earnings,
        pending_earnings=pending_earnings,
        top_product=top_product_name,
        platform_breakdown=platform_breakdown,
        location_breakdown=location_breakdown,
    )
