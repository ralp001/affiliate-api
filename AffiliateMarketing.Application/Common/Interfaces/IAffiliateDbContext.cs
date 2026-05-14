using AffiliateMarketing.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Common.Interfaces;

public interface IAffiliateDbContext
{
    DbSet<User> Users { get; }
    DbSet<AffiliateProfile> AffiliateProfiles { get; }
    DbSet<Product> Products { get; }
    DbSet<ReferralLink> ReferralLinks { get; }
    DbSet<ClickEvent> ClickEvents { get; }
    DbSet<Conversion> Conversions { get; }
    DbSet<AuditLog> AuditLogs { get; }

    Task<int> SaveChangesAsync(CancellationToken cancellationToken);
}