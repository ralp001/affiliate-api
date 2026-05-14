using AffiliateMarketing.Domain.Enums;

namespace AffiliateMarketing.Domain.Entities;

public sealed class Product
{
    public Guid Id { get; set; }
    public string Name { get; set; } = default!;
    public string Description { get; set; } = default!;

    public string ProductType { get; set; } = "Individual"; // Individual, Business, Enterprise
    public string SubscriptionPlan { get; set; } = "Starter";

    public CommissionType CommissionType { get; set; } = default!; // "Percentage" or "Fixed"
    public decimal CommissionValue { get; set; }
    public decimal BasePrice { get; set; }
    public string Currency { get; set; } = "NGN";
    public bool IsAvailableForAffiliates { get; set; } = true;
}