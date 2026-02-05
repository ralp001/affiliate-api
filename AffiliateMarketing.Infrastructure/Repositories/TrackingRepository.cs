using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories
{
    public sealed class TrackingRepository : ITrackingRepository
    {
        private readonly AffiliateDbContext _db;

        public TrackingRepository(AffiliateDbContext db)
        {
            _db = db;
        }

        public async Task RegisterClickAsync(
            string trackingId,
            string userAgent,
            string ipAddress,
            CancellationToken cancellationToken)
        {
            _db.ClickEvents.Add(new ClickEvent
            {
                Id = Guid.NewGuid(),
                TrackingId = trackingId,
                UserAgent = userAgent,
                IpAddress = ipAddress,
                ClickedAt = DateTime.UtcNow
            });

            await _db.SaveChangesAsync(cancellationToken);
        }

        public async Task<int> GetClickCountAsync(
            string trackingId,
            CancellationToken cancellationToken)
        {
            return await _db.ClickEvents
                .CountAsync(x => x.TrackingId == trackingId, cancellationToken);
        }
    }
}
