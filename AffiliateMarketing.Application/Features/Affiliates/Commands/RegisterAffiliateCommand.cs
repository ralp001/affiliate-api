using MediatR;

namespace AffiliateMarketing.Application.Features.Affiliates.Commands;

public record RegisterAffiliateCommand(
    Guid UserId,
    string PreferredTrackingId // e.g., "JIMMY-MARKETER"
) : IRequest<Guid>;