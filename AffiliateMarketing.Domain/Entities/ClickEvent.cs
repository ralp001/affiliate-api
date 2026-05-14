namespace AffiliateMarketing.Domain.Entities;

public sealed class ClickEvent
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string TrackingId { get; set; } = default!;
    public string IpAddress { get; set; } = default!;
    public string? UserAgent { get; set; }
    public string? Platform { get; set; }
    public Guid ProductId { get; set; }
    public DateTime ClickedAt { get; set; } = DateTime.UtcNow;
    //public Guid AffiliateUserId { get; set; }

    // --- High-Resolution Geo Data ---
    public string? CountryCode { get; set; }
    public string? City { get; set; }
    public string? Region { get; set; }
    public string? Location { get; set; } // Formatted string for dashboard display
}