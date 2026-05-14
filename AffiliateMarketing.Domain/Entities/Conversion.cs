namespace AffiliateMarketing.Domain.Entities;

public class Conversion
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid AffiliateUserId { get; set; } // The Marketer
    public Guid BuyerUserId { get; set; }     // The Customer
    public Guid ProductId { get; set; }
    public decimal SaleAmount { get; set; }
    public decimal CommissionEarned { get; set; }
    public string ReferralCode { get; set; } = default!;

    public string? CustomerCountry { get; set; } // Captured at checkout via IpInfo
    public string? ReferralSource { get; set; }  // e.g., "Twitter", "Email"

    public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
}