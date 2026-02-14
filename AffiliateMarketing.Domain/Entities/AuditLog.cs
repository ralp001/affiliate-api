public class AuditLog
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public string EntityName { get; set; } = default!;
    public string Action { get; set; } = default!;
    public string? OldValues { get; set; } // JSON String
    public string? NewValues { get; set; } // JSON String
    public string PerformedBy { get; set; } = "System_User";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}