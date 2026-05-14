using System.Collections.Concurrent;
using AffiliateMarketing.Application.Common.Security;

namespace Ticketing.Infrastructure.Security;

public class PermissionCache : IPermissionCache
{
    private readonly ConcurrentDictionary<string, HashSet<string>> _cache = new();

    private string BuildKey(string clearanceType, string clearanceLevel, string fieldPath)
        => $"{clearanceType}:{clearanceLevel}:{fieldPath}";

    public void SetPermissions(
        string clearanceType,
        string clearanceLevel,
        string fieldPath,
        IEnumerable<string> permissions)
    {
        var key = BuildKey(clearanceType, clearanceLevel, fieldPath);

        _cache[key] = new HashSet<string>(permissions);
    }

    public HashSet<string> GetPermissions(
        string clearanceType,
        string clearanceLevel,
        string fieldPath)
    {
        var key = BuildKey(clearanceType, clearanceLevel, fieldPath);

        return _cache.TryGetValue(key, out var perms)
            ? perms
            : new HashSet<string>();
    }

    public bool HasPermission(
        string clearanceType,
        string clearanceLevel,
        string fieldPath,
        string permission)
    {
        var perms = GetPermissions(clearanceType, clearanceLevel, fieldPath);

        return perms.Contains(permission);
    }
}