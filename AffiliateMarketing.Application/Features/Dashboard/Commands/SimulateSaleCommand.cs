using MediatR;

namespace AffiliateMarketing.Application.Features.Dashboard.Commands;

public record SimulateSaleCommand(
    Guid ProductId,
    string ReferralCode,
    decimal Amount,
    string Country) : IRequest<bool>;