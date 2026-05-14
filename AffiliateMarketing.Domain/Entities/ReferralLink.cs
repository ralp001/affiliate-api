namespace AffiliateMarketing.Domain.Entities;

public sealed class ReferralLink
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid AffiliateProfileId { get; set; }
    public Guid ProductId { get; set; }

    // The unique string in the URL (e.g., "startup-deal-jimmy")
    public string GeneratedCode { get; set; } = default!;

    // For Phase 7: Tracking if this link was for FB, IG, or YouTube
    public string? SourcePlatform { get; set; }

    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public AffiliateProfile AffiliateProfile { get; set; } = default!;
    public Product Product { get; set; } = default!;
}