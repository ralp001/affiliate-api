# Source: AffiliateMarketing.Application/Features/Dashboard/Dtos/DashboardSummaryDto.cs
from pydantic import BaseModel
from datetime import datetime


class AffiliatePerformanceSchema(BaseModel):
    username: str
    home_country: str
    created_at: datetime
    count: int
    revenue: float = 0.0


class CountryProductMetricSchema(BaseModel):
    country: str
    product_name: str
    count: int


class CountryMetricSchema(BaseModel):
    country_code: str
    click_count: int


class DashboardSummaryResponse(BaseModel):
    top_product_by_sales: str
    total_revenue: float
    top_country_by_visits: str
    top_country_by_purchases: str
    total_clicks: int
    top_affiliates_by_sales: list[AffiliatePerformanceSchema]
    top_affiliates_by_links: list[AffiliatePerformanceSchema]
    top_countries_with_products: list[CountryProductMetricSchema]
    geographic_breakdown: list[CountryMetricSchema]


class AffiliatePlatformMetric(BaseModel):
    platform: str
    clicks: int
    conversions: int


class MyDashboardResponse(BaseModel):
    total_clicks: int
    total_conversions: int
    confirmed_earnings: float
    pending_earnings: float
    top_product: str | None
    platform_breakdown: list[AffiliatePlatformMetric]
    location_breakdown: list[CountryMetricSchema]
