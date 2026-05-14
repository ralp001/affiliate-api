using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using AffiliateMarketing.Application.Abstractions;
using Affiliate.Application.Abstractions;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories;

public sealed class UserRepository : IUserRepository
{
    private readonly AffiliateDbContext _db;
    private readonly ILogService _logService;
    private readonly IMessageProducer _producer;

    public UserRepository(AffiliateDbContext db, ILogService logService, IMessageProducer producer)
    {
        _db = db;
        _logService = logService;
        _producer = producer;
    }

    public async Task AddAsync(User user, CancellationToken ct)
    {
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(user.PasswordHash);
        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);

        // BOSS REQUIREMENT: Fan-out the user creation to the central Logs API
        await _logService.LogAsync(user.Id, "User_Registration", "Success", $"User {user.Username} registered.");
        await _producer.PublishAsync("user-events", new { user.Id, user.Username, user.Role, Action = "Created" });
    }

    public async Task<User?> GetByUsernameAsync(string username, CancellationToken ct)
    {
        return await _db.Users.FirstOrDefaultAsync(x => x.Username == username, ct);
    }
}