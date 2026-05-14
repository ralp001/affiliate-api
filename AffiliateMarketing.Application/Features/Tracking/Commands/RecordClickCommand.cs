using MediatR;

namespace AffiliateMarketing.Application.Features.Tracking.Commands;

// We changed IRequest<bool> to IRequest<string> so we get the Redirect URL back
public record RecordClickCommand(
    string ReferralCode,
    string IpAddress,
    string? UserAgent = null,
    string? Platform = null
) : MediatR.IRequest<string>;