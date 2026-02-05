using MediatR;

namespace AffiliateMarketing.Application.Products.Commands
{
    public sealed record SetCommissionCommand(
        Guid ProductId,
        string Type,
        decimal Value
    ) : IRequest;
}
