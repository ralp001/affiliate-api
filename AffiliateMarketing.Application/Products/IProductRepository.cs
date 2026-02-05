using AffiliateMarketing.Domain.Entities;

namespace AffiliateMarketing.Application.Products
{
    public interface IProductRepository
    {
        Task AddAsync(Product product, CancellationToken cancellationToken);

        Task<Product> GetByIdAsync(
            Guid id,
            CancellationToken cancellationToken);

        Task UpdateAsync(
            Product product,
            CancellationToken cancellationToken);

        Task<IEnumerable<Product>> GetAllAsync(
            CancellationToken cancellationToken);
    }
}
