using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Application.Features.Dashboard.Dtos;
using AffiliateMarketing.Application.Features.Dashboard.Queries;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Features.Dashboard.Handlers;

public class GetDashboardSummaryHandler : IRequestHandler<GetDashboardSummaryQuery, DashboardSummaryDto>
{
    private readonly IAffiliateDbContext _context;

    public GetDashboardSummaryHandler(IAffiliateDbContext context) => _context = context;

    public async Task<DashboardSummaryDto> Handle(GetDashboardSummaryQuery request, CancellationToken ct)
    {
        // 1. Top performing product by sales
        var topProductData = await _context.Conversions
            .GroupBy(c => c.ProductId)
            .Select(g => new { ProductId = g.Key, Total = g.Sum(x => x.SaleAmount) })
            .OrderByDescending(x => x.Total)
            .FirstOrDefaultAsync(ct);

        string productName = "No Sales Yet";
        if (topProductData != null)
        {
            var p = await _context.Products.FindAsync(new object[] { topProductData.ProductId }, ct);
            productName = p?.Name ?? "Unknown Product";
        }

        // 2. Top country of visit (Clicks)
        var topVisitCountry = await _context.ClickEvents
            .Where(c => c.CountryCode != null)
            .GroupBy(c => c.CountryCode)
            .OrderByDescending(g => g.Count())
            .Select(g => g.Key)
            .FirstOrDefaultAsync(ct) ?? "N/A";

        // 3. Top country with highest purchases (Conversions)
        var topPurchaseCountry = await _context.Conversions
            .Where(c => c.CustomerCountry != null)
            .GroupBy(c => c.CustomerCountry)
            .OrderByDescending(g => g.Count())
            .Select(g => g.Key)
            .FirstOrDefaultAsync(ct) ?? "N/A";

        // 4. Top performing affiliate partners by SALES
        var topAffiliatesSalesData = await _context.Conversions
            .GroupBy(c => c.AffiliateUserId)
            .OrderByDescending(g => g.Count())
            .Take(5)
            .Select(g => new { Id = g.Key, SalesCount = g.Count(), Revenue = g.Sum(x => x.SaleAmount) })
            .ToListAsync(ct);

        var topAffiliatesBySales = new List<AffiliatePerformanceDto>();
        foreach (var item in topAffiliatesSalesData)
        {
            var user = await _context.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == item.Id, ct);
            if (user != null)
            {
                topAffiliatesBySales.Add(new AffiliatePerformanceDto(
                    user.Username, user.HomeCountry, user.CreatedAt, item.SalesCount, item.Revenue));
            }
        }

        // 5. Top performing affiliate by REFERRAL LINKS (Joining ClickEvents to ReferralLinks)
        var topAffiliatesLinksData = await (from click in _context.ClickEvents
                                            join link in _context.ReferralLinks on click.TrackingId equals link.GeneratedCode
                                            group click by link.AffiliateProfileId into g
                                            orderby g.Count() descending
                                            select new { ProfileId = g.Key, ClickCount = g.Count() })
                                           .Take(5)
                                           .ToListAsync(ct);

        var topAffiliatesByLinks = new List<AffiliatePerformanceDto>();
        foreach (var item in topAffiliatesLinksData)
        {
            var profile = await _context.AffiliateProfiles.AsNoTracking().FirstOrDefaultAsync(p => p.Id == item.ProfileId, ct);
            if (profile != null)
            {
                // Corrected field: UserId (as per your AffiliateProfile definition)
                var user = await _context.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == profile.UserId, ct);
                if (user != null)
                {
                    topAffiliatesByLinks.Add(new AffiliatePerformanceDto(
                        user.Username, user.HomeCountry, user.CreatedAt, item.ClickCount));
                }
            }
        }

        // 6. Top countries with products bought
        var countryProductMetricsRaw = await _context.Conversions
            .GroupBy(c => new { c.CustomerCountry, c.ProductId })
            .OrderByDescending(g => g.Count())
            .Take(5)
            .Select(g => new { g.Key.CustomerCountry, g.Key.ProductId, Count = g.Count() })
            .ToListAsync(ct);

        var countryProductMetrics = new List<CountryProductMetricDto>();
        foreach (var item in countryProductMetricsRaw)
        {
            var p = await _context.Products.FindAsync(new object[] { item.ProductId }, ct);
            countryProductMetrics.Add(new CountryProductMetricDto(
                item.CustomerCountry ?? "Unknown",
                p?.Name ?? "Unknown Product",
                item.Count));
        }

        // 7. Geographic Breakdown for Dashboard Visualization
        var geoData = await _context.ClickEvents
            .Where(c => c.CountryCode != null)
            .GroupBy(c => c.CountryCode)
            .Select(g => new CountryMetricDto(g.Key!, g.Count()))
            .ToListAsync(ct);

        return new DashboardSummaryDto(
            TopProductBySales: productName,
            TotalRevenue: await _context.Conversions.SumAsync(c => c.SaleAmount, ct),
            TopCountryByVisits: topVisitCountry,
            TopCountryByPurchases: topPurchaseCountry,
            TotalClicks: await _context.ClickEvents.CountAsync(ct),
            TopAffiliatesBySales: topAffiliatesBySales,
            TopAffiliatesByLinks: topAffiliatesByLinks,
            TopCountriesWithProducts: countryProductMetrics,
            GeographicBreakdown: geoData
        );
    }
}