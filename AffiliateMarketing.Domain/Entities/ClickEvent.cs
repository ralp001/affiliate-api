namespace AffiliateMarketing.Domain.Entities
{
    public sealed class ClickEvent
    {
        public Guid Id { get; set; }
        public required string TrackingId { get; set; }
        public required string UserAgent { get; set; }
        public required string IpAddress { get; set; }
        public DateTime ClickedAt { get; set; }
    }

}
