using AffiliateMarketing.Application.Common.Security;

namespace AffiliateMarketing.Infrastructure.Security;

public class PermissionService : IPermissionService
{
    private readonly ICurrentUserService _currentUser;
    private readonly IPermissionCache _cache;

    public PermissionService(
        ICurrentUserService currentUser,
        IPermissionCache cache)
    {
        _currentUser = currentUser;
        _cache = cache;
    }

    public bool HasPermission(string fieldPath, string action)
    {
        // 🔐 Ensure authenticated
        if (!_currentUser.IsAuthenticated)
            return false;

        // 🔍 Determine user type
        if (_currentUser.IsInternal)
            return CheckInternal(fieldPath, action);

        if (_currentUser.IsExternal)
            return CheckExternal(fieldPath, action);

        return false;
    }

    // =========================
    // 🔐 INTERNAL USERS (Kafka-driven)
    // =========================
    private bool CheckInternal(string fieldPath, string action)
    {
        var clearanceType = _currentUser.ClearanceType;
        var clearanceLevel = _currentUser.ClearanceLevel;

        if (string.IsNullOrEmpty(clearanceType) ||
            string.IsNullOrEmpty(clearanceLevel))
            return false;

        return _cache.HasPermission(
            clearanceType,
            clearanceLevel,
            fieldPath,
            action
        );
    }

    // =========================
    // 🌐 EXTERNAL USERS (Computed)
    // =========================
    private bool CheckExternal(string fieldPath, string action)
    {
        var role = _currentUser.ResponsibilityCategory;
        var tier = _currentUser.ProductTier;

        if (string.IsNullOrEmpty(role) || string.IsNullOrEmpty(tier))
            return false;

        // =========================
        // 🔥 ROLE-BASED OVERRIDE
        // =========================
        if (role == "CyberAdmin" || role == "BranchAdmin")
        {
            return true; // Full system access
        }

        // =========================
        // 📦 PRODUCT TIER RULES
        // =========================

        // 🧍 INDIVIDUAL
        if (tier == "Individual")
        {
            return fieldPath switch
            {
                "affiliate.link.create" => action == "create",
                "affiliate.link.read" => action == "read",

                "affiliate.dashboard.read" => action == "read",
                "affiliate.commission.read" => action == "read",

                _ => false
            };
        }

        // 🏢 BUSINESS
        if (tier == "Business")
        {
            return fieldPath switch
            {
                "affiliate.link.create" => action == "create",
                "affiliate.link.read" => action == "read",

                "affiliate.dashboard.read" => action == "read",
                "affiliate.commission.read" => action == "read",

                "affiliate.payout.request" => action == "create",
                "affiliate.payout.read" => action == "read",

                _ => false
            };
        }

        // 🏦 ENTERPRISE
        if (tier == "Enterprise")
        {
            return true; // Full access
        }

        return false;
    }
}