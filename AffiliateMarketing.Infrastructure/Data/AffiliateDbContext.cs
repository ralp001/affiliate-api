using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Domain.Enums;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Data;

public sealed class AffiliateDbContext : DbContext, IAffiliateDbContext
{
    public AffiliateDbContext(DbContextOptions<AffiliateDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Product> Products => Set<Product>();
    public DbSet<AffiliateProfile> AffiliateProfiles => Set<AffiliateProfile>();
    public DbSet<ClickEvent> ClickEvents => Set<ClickEvent>();
    public DbSet<ReferralLink> ReferralLinks => Set<ReferralLink>();
    public DbSet<Conversion> Conversions => Set<Conversion>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();
    public DbSet<UserClearance> UserClearances => Set<UserClearance>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // ---------- 1. PERFORMANCE INDEXES ----------
        modelBuilder.Entity<User>().HasIndex(x => x.Username).IsUnique();
        modelBuilder.Entity<AffiliateProfile>().HasIndex(x => x.TrackingId).IsUnique();
        modelBuilder.Entity<ClickEvent>().HasIndex(x => x.CountryCode);
        modelBuilder.Entity<Conversion>().HasIndex(x => x.CustomerCountry);

        // ---------- 2. PRECISION CONFIG (FinTech Grade) ----------
        modelBuilder.Entity<Product>().Property(x => x.CommissionValue).HasPrecision(18, 2);
        modelBuilder.Entity<Product>().Property(x => x.BasePrice).HasPrecision(18, 2);
        modelBuilder.Entity<Conversion>().Property(x => x.SaleAmount).HasPrecision(18, 2);
        modelBuilder.Entity<Conversion>().Property(x => x.CommissionEarned).HasPrecision(18, 2);

        // ---------- 3. GLOBAL SEED DATA ----------
        var staticDate = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc);

        // GUIDs - Nigeria
        var userNG = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var profileNG = Guid.Parse("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb");

        // GUIDs - Australia
        var userAU = Guid.Parse("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa");
        var profileAU = Guid.Parse("cccccccc-cccc-cccc-cccc-cccccccccccc");

        // Product GUIDs
        var idexGuid = Guid.Parse("33333333-3333-3333-3333-333333333333");
        var nixusGuid = Guid.Parse("44444444-4444-4444-4444-444444444444");

        // A. Seed Users (Global Partners)
        modelBuilder.Entity<User>().HasData(
            new User { Id = userNG, Username = "Jimmy_Affiliate", PasswordHash = "hash", Role = "Affiliate", HomeCountry = "Nigeria", CreatedAt = staticDate },
            new User { Id = userAU, Username = "Aussie_Partner", PasswordHash = "hash", Role = "Affiliate", HomeCountry = "Australia", CreatedAt = staticDate.AddDays(5) }
        );

        // B. Seed Products (Multi-Tier)
        modelBuilder.Entity<Product>().HasData(
            new Product
            {
                Id = idexGuid,
                Name = "Emutare Idex",
                Description = "Individual tracking",
                ProductType = "Individual",
                SubscriptionPlan = "Gold",
                BasePrice = 5000,
                Currency = "NGN",
                CommissionType = CommissionType.Percentage,
                CommissionValue = 10
            },
            new Product
            {
                Id = nixusGuid,
                Name = "Nixus",
                Description = "Enterprise management",
                ProductType = "Business",
                SubscriptionPlan = "Platinum",
                BasePrice = 25000,
                Currency = "NGN",
                CommissionType = CommissionType.Percentage,
                CommissionValue = 15
            }
        );

        // C. Seed Affiliate Profiles
        modelBuilder.Entity<AffiliateProfile>().HasData(
            new AffiliateProfile { Id = profileNG, UserId = userNG, TrackingId = "JIMMY_PROFILE", CreatedAt = staticDate, IsActive = true },
            new AffiliateProfile { Id = profileAU, UserId = userAU, TrackingId = "AUSSIE_PROFILE", CreatedAt = staticDate.AddDays(5), IsActive = true }
        );

        // D. Seed Referral Links (The Bridges)
        modelBuilder.Entity<ReferralLink>().HasData(
            new ReferralLink { Id = Guid.Parse("77777777-7777-7777-7777-777777777777"), AffiliateProfileId = profileNG, ProductId = idexGuid, GeneratedCode = "JIMMY_DEMO", IsActive = true, CreatedAt = staticDate },
            new ReferralLink { Id = Guid.Parse("88888888-8888-8888-8888-888888888888"), AffiliateProfileId = profileAU, ProductId = nixusGuid, GeneratedCode = "AUSSIE_CODE", IsActive = true, CreatedAt = staticDate.AddDays(5) }
        );

        // E. Seed Click Events (Geo-Visuals)
        modelBuilder.Entity<ClickEvent>().HasData(
            new ClickEvent { Id = Guid.Parse("55555555-5555-5555-5555-555555555555"), TrackingId = "JIMMY_DEMO", IpAddress = "102.89.1.1", ClickedAt = staticDate, ProductId = idexGuid, CountryCode = "NG", City = "Onitsha", Location = "Onitsha, NG" },
            new ClickEvent { Id = Guid.Parse("99999999-9999-9999-9999-999999999999"), TrackingId = "AUSSIE_CODE", IpAddress = "1.1.1.1", ClickedAt = staticDate.AddDays(6), ProductId = nixusGuid, CountryCode = "AU", City = "Sydney", Location = "Sydney, AU" }
        );
    }

    public override Task<int> SaveChangesAsync(CancellationToken ct = default)
        => base.SaveChangesAsync(ct);
}

public class UserClearance
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public string Role { get; set; } = default!;
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}