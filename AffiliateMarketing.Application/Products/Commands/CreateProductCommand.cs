using MediatR;

namespace AffiliateMarketing.Application.Products.Commands
{
    public sealed record CreateProductCommand(string Name) : IRequest;
}
