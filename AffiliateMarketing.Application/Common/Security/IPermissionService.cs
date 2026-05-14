namespace AffiliateMarketing.Application.Common.Security;

public interface IPermissionService
{
    /// <summary>
    /// Checks if the current user has permission to perform an action on a given field/resource.
    /// </summary>
    /// <param name="fieldPath">The resource path (e.g. "affiliate.link.create")</param>
    /// <param name="action">The action (e.g. "create", "read")</param>
    /// <returns>True if allowed, otherwise false</returns>
    bool HasPermission(string fieldPath, string action);
}