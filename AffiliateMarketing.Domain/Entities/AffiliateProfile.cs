namespace AffiliateMarketing.Domain.Entities
{
    public sealed class AffiliateProfile
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string TrackingId { get; set; }
    public DateTime CreatedAt { get; set; }
}
}


