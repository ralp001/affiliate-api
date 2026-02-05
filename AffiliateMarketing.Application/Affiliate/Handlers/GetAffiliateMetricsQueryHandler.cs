using AffiliateMarketing.Application.Affiliate.Queries;
using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Contracts.Affiliate;
using MediatR;

namespace AffiliateMarketing.Application.Affiliate.Handlers
{
    public sealed class GetAffiliateMetricsQueryHandler
        : IRequestHandler<GetAffiliateMetricsQuery, AffiliateMetricsResponse>
    {
        private readonly ITrackingRepository _trackingRepository;

        public GetAffiliateMetricsQueryHandler(ITrackingRepository trackingRepository)
        {
            _trackingRepository = trackingRepository;
        }

        public async Task<AffiliateMetricsResponse> Handle(
            GetAffiliateMetricsQuery request,
            CancellationToken cancellationToken)
        {
            var clicks = await _trackingRepository
                .GetClickCountAsync(request.TrackingId, cancellationToken);

            return new AffiliateMetricsResponse
            {
                TotalClicks = clicks
            };
        }
    }
}
