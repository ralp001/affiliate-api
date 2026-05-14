using AffiliateMarketing.Domain.Entities;

namespace AffiliateMarketing.Application.Identity;

public interface IUserRepository
{
    Task AddAsync(User user, CancellationToken cancellationToken);
    Task<User?> GetByUsernameAsync(string username, CancellationToken cancellationToken);
}