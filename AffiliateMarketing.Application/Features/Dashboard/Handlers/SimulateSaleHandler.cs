using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Application.Features.Dashboard.Commands;
using AffiliateMarketing.Domain.Entities;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Features.Dashboard.Handlers;

public class SimulateSaleHandler : IRequestHandler<SimulateSaleCommand, bool>
{
    private readonly IAffiliateDbContext _context;

    public SimulateSaleHandler(IAffiliateDbContext context) => _context = context;

    public async Task<bool> Handle(SimulateSaleCommand request, CancellationToken ct)
    {
        // 1. Find the Affiliate associated with this referral code
        var link = await _context.ReferralLinks
            .FirstOrDefaultAsync(l => l.GeneratedCode == request.ReferralCode, ct);

        if (link == null) return false;

        // 2. Find the Profile to get the UserId
        var profile = await _context.AffiliateProfiles
            .FirstOrDefaultAsync(p => p.Id == link.AffiliateProfileId, ct);

        if (profile == null) return false;

        // 3. Create the Conversion (The Sale)
        var conversion = new Conversion
        {
            Id = Guid.NewGuid(),
            ProductId = request.ProductId,
            AffiliateUserId = profile.UserId, // The person getting paid
            SaleAmount = request.Amount,
            CommissionEarned = request.Amount * 0.10m, // 10% demo commission
            CustomerCountry = request.Country,
            ProcessedAt = DateTime.UtcNow,
            ReferralCode = request.ReferralCode
        };

        _context.Conversions.Add(conversion);
        await _context.SaveChangesAsync(ct);
        return true;
    }
}