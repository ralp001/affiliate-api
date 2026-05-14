using AffiliateMarketing.Application.Common.Security;
using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Domain.Entities;

namespace AffiliateMarketing.Infrastructure.Security;

public class UserProjectionService : IUserProjectionService
{
    private readonly ICurrentUserService _currentUser;
    private readonly IUserRepository _userRepository;

    public UserProjectionService(
        ICurrentUserService currentUser,
        IUserRepository userRepository)
    {
        _currentUser = currentUser;
        _userRepository = userRepository;
    }

    public async Task SyncExternalUserAsync(CancellationToken cancellationToken)
    {
        if (!_currentUser.IsExternal)
            return;

        var user = new User
        {
            Id = _currentUser.UserUuid,
            ResponsibilityCategory = _currentUser.ResponsibilityCategory ?? "Affiliate",
            ProductTier = _currentUser.ProductTier ?? "Individual",
            IsActive = true
        };

        await _userRepository.UpsertAsync(user, cancellationToken);
    }
}