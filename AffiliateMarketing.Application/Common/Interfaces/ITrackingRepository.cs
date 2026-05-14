namespace AffiliateMarketing.Application.Tracking;

public interface ITrackingRepository
{
    Task RegisterClickAsync(string trackingId, string userAgent, string ipAddress, CancellationToken cancellationToken);
    Task<int> GetClickCountAsync(string trackingId, CancellationToken cancellationToken);
}