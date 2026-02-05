using AffiliateMarketing.Application.Products.Commands;
using AffiliateMarketing.Domain.Entities;
using MediatR;

namespace AffiliateMarketing.Application.Products.Handlers
{
    public sealed class CreateProductCommandHandler
        : IRequestHandler<CreateProductCommand>
    {
        private readonly IProductRepository _productRepository;

        public CreateProductCommandHandler(IProductRepository productRepository)
        {
            _productRepository = productRepository;
        }

        public async Task Handle(
            CreateProductCommand request,
            CancellationToken cancellationToken)
        {
            var product = new Product
            {
                Id = Guid.NewGuid(),
                Name = request.Name,

                // Safe skeletal defaults
                CommissionType = "percentage",
                CommissionValue = 0m
            };

            await _productRepository.AddAsync(product, cancellationToken);
        }
    }
}
