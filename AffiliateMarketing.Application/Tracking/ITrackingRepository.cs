namespace AffiliateMarketing.Application.Tracking
{
    public interface ITrackingRepository
    {
        Task<int> GetClickCountAsync(
            string trackingId,
            CancellationToken cancellationToken);

        Task RegisterClickAsync(
            string trackingId,
            string userAgent,
            string ipAddress,
            CancellationToken cancellationToken);
    }
}
