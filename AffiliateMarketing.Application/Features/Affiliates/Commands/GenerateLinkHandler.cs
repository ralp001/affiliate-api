using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Domain.Entities;
using MediatR;

public class GenerateLinkHandler : IRequestHandler<GenerateLinkCommand, string>
{
    private readonly IAffiliateDbContext _context;

    public GenerateLinkHandler(IAffiliateDbContext context) => _context = context;

    public async Task<string> Handle(GenerateLinkCommand request, CancellationToken ct)
    {
        var profile = await _context.AffiliateProfiles.FindAsync(request.AffiliateProfileId);
        var product = await _context.Products.FindAsync(request.ProductId);

        if (profile == null || product == null) throw new Exception("Invalid IDs provided.");

        // Create the unique referral code: TrackingId + ProductId fragment
        var uniqueCode = $"{profile.TrackingId}-{product.Name.Substring(0, 3).ToUpper()}-{Guid.NewGuid().ToString().Substring(0, 4)}";

        var link = new ReferralLink
        {
            Id = Guid.NewGuid(),
            AffiliateProfileId = profile.Id,
            ProductId = product.Id,
            GeneratedCode = uniqueCode,
            SourcePlatform = request.SourcePlatform,
            CreatedAt = DateTime.UtcNow
        };

        _context.ReferralLinks.Add(link);
        await _context.SaveChangesAsync(ct);

        return uniqueCode; // This is what goes into the URL
    }
}