using AffiliateMarketing.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Data
{
    public sealed class AffiliateDbContext : DbContext
    {
        public AffiliateDbContext(DbContextOptions<AffiliateDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users => Set<User>();
        public DbSet<Product> Products => Set<Product>();
        public DbSet<AffiliateProfile> AffiliateProfiles => Set<AffiliateProfile>();
        public DbSet<ClickEvent> ClickEvents => Set<ClickEvent>();

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // ---------- INDEXES ----------
            modelBuilder.Entity<User>()
                .HasIndex(x => x.Username)
                .IsUnique();

            modelBuilder.Entity<AffiliateProfile>()
                .HasIndex(x => x.TrackingId)
                .IsUnique();

            // ---------- PRECISION ----------
            modelBuilder.Entity<Product>()
                .Property(x => x.CommissionValue)
                .HasPrecision(18, 2);

            // ---------- SEED DATA (DETERMINISTIC) ----------

            var demoUserId = Guid.Parse("11111111-1111-1111-1111-111111111111");
            var affiliateProfileId = Guid.Parse("33333333-3333-3333-3333-333333333333");
            var productId = Guid.Parse("22222222-2222-2222-2222-222222222222");

            var seedTime = new DateTime(2024, 1, 1, 12, 0, 0, DateTimeKind.Utc);

            modelBuilder.Entity<User>().HasData(new User
            {
                Id = demoUserId,
                Username = "demo_affiliate",
                PasswordHash = "$2a$11$BMPxjYU01aj1TVGEyqnHaejKA9aZyXnDCKl5ER4jb7h28goYYGczC",
                Role = "Affiliate",
                CreatedAt = seedTime
            });

            modelBuilder.Entity<AffiliateProfile>().HasData(new AffiliateProfile
            {
                Id = affiliateProfileId,
                UserId = demoUserId,
                TrackingId = "DEMO123",
                CreatedAt = seedTime
            });

            modelBuilder.Entity<Product>().HasData(new Product
            {
                Id = productId,
                Name = "Startup Plan",
                CommissionType = "percentage",
                CommissionValue = 60m
            });

            modelBuilder.Entity<ClickEvent>().HasData(
                new ClickEvent
                {
                    Id = Guid.Parse("44444444-4444-4444-4444-444444444444"),
                    TrackingId = "DEMO123",
                    UserAgent = "Mozilla/5.0",
                    IpAddress = "127.0.0.1",
                    ClickedAt = seedTime.AddMinutes(-10)
                },
                new ClickEvent
                {
                    Id = Guid.Parse("55555555-5555-5555-5555-555555555555"),
                    TrackingId = "DEMO123",
                    UserAgent = "Chrome",
                    IpAddress = "127.0.0.1",
                    ClickedAt = seedTime.AddMinutes(-5)
                }
            );
        }
    }
}