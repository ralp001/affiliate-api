namespace AffiliateMarketing.Domain.Entities
{
    public sealed class Product
{
    public Guid Id { get; set; }
    public required string Name { get; set; }
    public required string CommissionType { get; set; }
    public decimal CommissionValue { get; set; }
}
}
