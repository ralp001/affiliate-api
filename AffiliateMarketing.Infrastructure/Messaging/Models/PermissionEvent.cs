namespace AffiliateMarketing.Infrastructure.Messaging.Models;

public class PermissionEvent
{
    public string EventType { get; set; } = default!;
    public string Action { get; set; } = default!;
    public string ApiName { get; set; } = default!;

    public string ClearanceType { get; set; } = default!;
    public string ClearanceLevel { get; set; } = default!;

    public DataField? DataField { get; set; }
    public List<DataField>? DataFields { get; set; }

    public List<ClearanceLevelData>? ClearanceLevels { get; set; }
}

public class DataField
{
    public string FieldPath { get; set; } = default!;
    public List<string> Permissions { get; set; } = new();
}

public class ClearanceLevelData
{
    public string LevelName { get; set; } = default!;
    public List<DataField> DataFields { get; set; } = new();
}