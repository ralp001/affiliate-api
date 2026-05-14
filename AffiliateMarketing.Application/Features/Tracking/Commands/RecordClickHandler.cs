using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Application.Features.Tracking.Commands;
using AffiliateMarketing.Domain.Entities;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Features.Tracking.Handlers;

public class RecordClickHandler : IRequestHandler<RecordClickCommand, string>
{
    private readonly IAffiliateDbContext _context;
    private readonly IGeoLocationService _geoService; // NEW: The Intelligence Layer

    public RecordClickHandler(IAffiliateDbContext context, IGeoLocationService geoService)
    {
        _context = context;
        _geoService = geoService;
    }

    public async Task<string> Handle(RecordClickCommand request, CancellationToken ct)
    {
        // 1. Fetch the link and Product
        var link = await _context.ReferralLinks
            .Include(l => l.Product)
            .FirstOrDefaultAsync(l => l.GeneratedCode == request.ReferralCode, ct);

        if (link == null) return "https://emutare.com/404"; // Professional fallback

        // 2. Antigravity Intelligence: Get Real-Time Geo Data from IpInfo
        var geo = await _geoService.GetLocationAsync(request.IpAddress, ct);

        // 3. Create the Enhanced Click Event
        var click = new ClickEvent
        {
            Id = Guid.NewGuid(),
            TrackingId = request.ReferralCode,
            IpAddress = request.IpAddress,
            UserAgent = request.UserAgent ?? "Unknown",
            Platform = request.Platform ?? "Direct",
            ProductId = link.ProductId,
            ClickedAt = DateTime.UtcNow,

            // Dashboard-Ready Fields (Your Boss's Requirements)
            CountryCode = geo.CountryCode,
            City = geo.City,
            Region = geo.Region,
            Location = $"{geo.City}, {geo.CountryCode}" // Combined for quick display
        };

        _context.ClickEvents.Add(click);

        // 4. Save to PostgreSQL (Local Docker)
        await _context.SaveChangesAsync(ct);

        // 5. Return the Destination URL
        return $"https://emutare.com/products/{link.ProductId}?ref={request.ReferralCode}";
    }
}