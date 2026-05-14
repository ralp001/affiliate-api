namespace AffiliateMarketing.Application.Common.Security
{
    public interface IUserProjectionService
    {
        Task SyncExternalUserAsync(CancellationToken cancellationToken);
    }
}
