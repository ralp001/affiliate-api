namespace AffiliateMarketing.Contracts.Affiliate
{
    public sealed class AffiliateProductResponse
    {
        public required string ProductName { get; init; }
        public required string CommissionType { get; init; }
        public decimal CommissionValue { get; init; }
    }
}
