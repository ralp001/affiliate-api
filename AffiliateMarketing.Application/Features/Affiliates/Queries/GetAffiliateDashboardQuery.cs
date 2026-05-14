using MediatR;
using AffiliateMarketing.Application.Common.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Features.Affiliates.Queries;

public record GetAffiliateDashboardQuery(Guid AffiliateUserId) : IRequest<List<AffiliateLinkDto>>;

public class GetAffiliateDashboardHandler : IRequestHandler<GetAffiliateDashboardQuery, List<AffiliateLinkDto>>
{
    private readonly IAffiliateDbContext _context;
    public GetAffiliateDashboardHandler(IAffiliateDbContext context) => _context = context;

    public async Task<List<AffiliateLinkDto>> Handle(GetAffiliateDashboardQuery request, CancellationToken ct)
    {
        return await _context.ReferralLinks
            .Where(l => l.AffiliateProfile.UserId == request.AffiliateUserId)
            .Select(l => new AffiliateLinkDto(
                l.Product.Name,
                l.GeneratedCode,
                l.SourcePlatform ?? "General",
                l.CreatedAt))
            .ToListAsync(ct);
    }
}

public record AffiliateLinkDto(string ProductName, string Code, string Platform, DateTime CreatedAt);