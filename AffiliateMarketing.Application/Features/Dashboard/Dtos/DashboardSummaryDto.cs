namespace AffiliateMarketing.Application.Features.Dashboard.Dtos;

// THE SINGLE SOURCE OF TRUTH FOR YOUR DASHBOARD
public record DashboardSummaryDto(
    string TopProductBySales,
    decimal TotalRevenue,
    string TopCountryByVisits,
    string TopCountryByPurchases,
    int TotalClicks,
    List<AffiliatePerformanceDto> TopAffiliatesBySales,
    List<AffiliatePerformanceDto> TopAffiliatesByLinks,
    List<CountryProductMetricDto> TopCountriesWithProducts,
    List<CountryMetricDto> GeographicBreakdown
);

public record CountryMetricDto(string CountryCode, int Count);

public record AffiliatePerformanceDto(
    string Name,
    string Country,
    DateTime JoinedAt,
    int Count,           // Represents Sales or Links depending on the list
    decimal TotalRevenue = 0
);

public record CountryProductMetricDto(
    string Country,
    string ProductName,
    int PurchaseCount
);