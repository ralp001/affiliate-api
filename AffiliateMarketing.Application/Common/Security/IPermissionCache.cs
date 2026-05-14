namespace AffiliateMarketing.Application.Common.Security;

public interface IPermissionCache
{
    void SetPermissions(
        string clearanceType,
        string clearanceLevel,
        string fieldPath,
        IEnumerable<string> permissions);

    HashSet<string> GetPermissions(
        string clearanceType,
        string clearanceLevel,
        string fieldPath);

    bool HasPermission(
        string clearanceType,
        string clearanceLevel,
        string fieldPath,
        string permission);
}