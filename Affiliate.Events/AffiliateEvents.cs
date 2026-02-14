using MediatR;

namespace Affiliate.Events;

// Captures new sign-ups
public record AffiliateRegisteredEvent : INotification
{
    public Guid AffiliateId { get; init; }
    public string BusinessName { get; init; } = default!;
    public string Email { get; init; } = default!;
    public string Region { get; init; } = default!; // e.g., Nigeria, USA
    public DateTime RegisteredAt { get; init; } = DateTime.UtcNow;
}

// Captures commission changes (The "Data Type" requirement)
public record CommissionUpdatedEvent : INotification
{
    public Guid AffiliateId { get; init; }
    public decimal NewRate { get; init; }
    public string Currency { get; init; } = "USD";
    public string UpdatedBy { get; init; } = default!;
    public DateTime EffectiveDate { get; init; } = DateTime.UtcNow;
}

public record UserPermissionUpdatedEvent
{
    public Guid UserId { get; init; }
    public string NewRole { get; init; } = default!;
    public string Reason { get; init; } = default!;
    public DateTime ChangedAt { get; init; } = DateTime.UtcNow;
}