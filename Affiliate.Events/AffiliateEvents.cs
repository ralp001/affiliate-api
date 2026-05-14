using MediatR;

namespace Affiliate.Events;

// --- SCHEMA DISCOVERY (The Enrollment Event - Automated for the Boss) ---
public class SchemaDiscoveryEvent : INotification
{
    public string api_name { get; set; } = "affiliate-marketing-api"; // Unique for this service
    public List<TableSchema> tables { get; set; } = new();
    public string hash { get; set; } = string.Empty;
    public string timestamp { get; set; } = DateTime.UtcNow.ToString("o");
}

public class TableSchema
{
    public string table_name { get; set; } = default!;
    public List<DataTypeInfo> data_types { get; set; } = new();
}

public class DataTypeInfo
{
    // CRITICAL: Property names must match Chibuikem's UI contract
    public string field_name { get; set; } = string.Empty;
    public string field_type { get; set; } = string.Empty;
}
// --- BUSINESS EVENTS (PascalCase - Handled by Global SnakeCase Policy) ---

// 1. New Affiliate Sign-up
public record AffiliateRegisteredEvent : INotification
{
    public Guid AffiliateId { get; init; }
    public string BusinessName { get; init; } = default!;
    public string Email { get; init; } = default!;
    public string Region { get; init; } = default!;
    public DateTime RegisteredAt { get; init; } = DateTime.UtcNow;
}

// 2. Commission Rate Changes (Data Type Requirement)
public record CommissionUpdatedEvent : INotification
{
    public Guid AffiliateId { get; init; }
    public decimal NewRate { get; init; }
    public string Currency { get; init; } = "NGN";
    public string UpdatedBy { get; init; } = default!;
    public DateTime EffectiveDate { get; init; } = DateTime.UtcNow;
}

// 3. Permission Sync (Fan-out to Identity)
public record UserPermissionUpdatedEvent : INotification
{
    public Guid UserId { get; init; }
    public string NewRole { get; init; } = default!;
    public string Reason { get; init; } = default!;
    public DateTime ChangedAt { get; init; } = DateTime.UtcNow;
}