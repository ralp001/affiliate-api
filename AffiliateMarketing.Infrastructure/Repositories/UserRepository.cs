using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories
{
    public sealed class UserRepository : IUserRepository
    {
        private readonly AffiliateDbContext _db;

        public UserRepository(AffiliateDbContext db)
        {
            _db = db;
        }

        public async Task AddAsync(User user, CancellationToken cancellationToken)
        {
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(user.PasswordHash);

            _db.Users.Add(user);
            await _db.SaveChangesAsync(cancellationToken);
        }

        public async Task<User?> GetByUsernameAsync(
            string username,
            CancellationToken cancellationToken)
        {
            return await _db.Users
                .FirstOrDefaultAsync(x => x.Username == username, cancellationToken);
        }
    }
}
