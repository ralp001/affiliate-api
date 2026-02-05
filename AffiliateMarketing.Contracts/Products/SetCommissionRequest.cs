namespace AffiliateMarketing.Contracts.Products
{
    public sealed class SetCommissionRequest
    {
        public required string Type { get; init; }   // percentage | fixed
        public decimal Value { get; init; }
    }
}
