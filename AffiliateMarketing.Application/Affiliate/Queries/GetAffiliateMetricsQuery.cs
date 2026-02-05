using MediatR;
using AffiliateMarketing.Contracts.Affiliate;

namespace AffiliateMarketing.Application.Affiliate.Queries
{
    public sealed record GetAffiliateMetricsQuery(string TrackingId)
        : IRequest<AffiliateMetricsResponse>;
}
