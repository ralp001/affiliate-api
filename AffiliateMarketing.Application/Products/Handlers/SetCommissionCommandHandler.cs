using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Application.Products.Commands;
using MediatR;

namespace AffiliateMarketing.Application.Products.Handlers
{
    public sealed class SetCommissionCommandHandler
        : IRequestHandler<SetCommissionCommand>
    {
        private readonly IProductRepository _repo;

        public SetCommissionCommandHandler(IProductRepository repo)
        {
            _repo = repo;
        }

        public async Task Handle(SetCommissionCommand request,
            CancellationToken cancellationToken)
        {
            var product = await _repo.GetByIdAsync(
                request.ProductId, cancellationToken);

            product.CommissionType = request.Type;
            product.CommissionValue = request.Value;

            await _repo.UpdateAsync(product, cancellationToken);
        }
    }
}
