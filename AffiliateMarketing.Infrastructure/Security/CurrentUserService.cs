using AffiliateMarketing.Application.Common.Security;
using Microsoft.AspNetCore.Http;
using System.Security.Claims;

namespace AffiliateMarketing.Infrastructure.Security;

public class CurrentUserService : ICurrentUserService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    private ClaimsPrincipal? User => _httpContextAccessor.HttpContext?.User;

    public bool IsAuthenticated =>
        User?.Identity?.IsAuthenticated ?? false;

    public Guid UserUuid
    {
        get
        {
            var value = User?.FindFirstValue("sub");

            if (string.IsNullOrEmpty(value))
                throw new UnauthorizedAccessException("User UUID not found");

            if (!Guid.TryParse(value, out var guid))
                throw new UnauthorizedAccessException("Invalid User UUID format");

            return guid;
        }
    }

    public string Issuer =>
        User?.FindFirstValue("iss") ?? "unknown";

    public bool IsInternal => Issuer == AuthConstants.InternalIssuer;
    public bool IsExternal => Issuer == AuthConstants.ExternalIssuer;

    public string? ClearanceType =>
        User?.FindFirstValue("clearance_type");

    public string? ClearanceLevel =>
        User?.FindFirstValue("clearance_level");

    public string? ResponsibilityCategory =>
        User?.FindFirstValue("responsibility_category");

    public string? ProductTier =>
        User?.FindFirstValue("product_tier");
}