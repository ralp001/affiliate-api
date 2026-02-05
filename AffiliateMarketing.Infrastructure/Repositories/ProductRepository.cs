using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories
{
    public sealed class ProductRepository : IProductRepository
    {
        private readonly AffiliateDbContext _db;

        public ProductRepository(AffiliateDbContext db)
        {
            _db = db;
        }

        public async Task AddAsync(Product product, CancellationToken cancellationToken)
        {
            _db.Products.Add(product);
            await _db.SaveChangesAsync(cancellationToken);
        }

        public async Task<IEnumerable<Product>> GetAllAsync(
            CancellationToken cancellationToken)
        {
            return await _db.Products.ToListAsync(cancellationToken);
        }

        public async Task<Product> GetByIdAsync(
     Guid id,
     CancellationToken cancellationToken)
        {
            return await _db.Products
                .FirstAsync(p => p.Id == id, cancellationToken);
        }

        public async Task UpdateAsync(
            Product product,
            CancellationToken cancellationToken)
        {
            _db.Products.Update(product);
            await _db.SaveChangesAsync(cancellationToken);
        }


    }
}
