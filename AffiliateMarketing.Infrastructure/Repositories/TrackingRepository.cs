using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using Affiliate.Application.Abstractions;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories;

public sealed class TrackingRepository : ITrackingRepository
{
    private readonly AffiliateDbContext _db;
    private readonly IMessageProducer _producer;

    public TrackingRepository(AffiliateDbContext db, IMessageProducer producer)
    {
        _db = db;
        _producer = producer;
    }

    public async Task RegisterClickAsync(string trackingId, string userAgent, string ipAddress, CancellationToken ct)
    {
        var click = new ClickEvent
        {
            Id = Guid.NewGuid(),
            TrackingId = trackingId,
            UserAgent = userAgent,
            IpAddress = ipAddress,
            ClickedAt = DateTime.UtcNow
        };

        _db.ClickEvents.Add(click);
        await _db.SaveChangesAsync(ct);

        // Phase 7: Fan-out click data for Centralized Analytics
        await _producer.PublishAsync("affiliate.clicks", new
        {
            click.TrackingId,
            click.IpAddress,
            click.ClickedAt,
            ApiSource = "AffiliateMarketing_API"
        });
    }

    public async Task<int> GetClickCountAsync(string trackingId, CancellationToken ct)
    {
        return await _db.ClickEvents.CountAsync(x => x.TrackingId == trackingId, ct);
    }
}