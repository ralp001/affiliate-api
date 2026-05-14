namespace AffiliateMarketing.Application.Common.Security;

public interface ICurrentUserService
{
    Guid UserUuid { get; }
    string Issuer { get; }

    bool IsAuthenticated { get; }

    bool IsInternal { get; }
    bool IsExternal { get; }

    string? ClearanceType { get; }
    string? ClearanceLevel { get; }

    string? ResponsibilityCategory { get; }
    string? ProductTier { get; }
}