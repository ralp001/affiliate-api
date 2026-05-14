using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Data;
using Affiliate.Application.Abstractions;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Infrastructure.Repositories;

public sealed class ProductRepository : IProductRepository
{
    private readonly AffiliateDbContext _db;
    private readonly IMessageProducer _producer;

    public ProductRepository(AffiliateDbContext db, IMessageProducer producer)
    {
        _db = db;
        _producer = producer;
    }

    public async Task AddAsync(Product product, CancellationToken ct)
    {
        _db.Products.Add(product);
        await _db.SaveChangesAsync(ct);

        // BOSS REQUIREMENT: Fan-out to notify other APIs of the new product
        await _producer.PublishAsync("affiliate.products.created", product);
    }

    public async Task<IEnumerable<Product>> GetAllAsync(CancellationToken ct) =>
        await _db.Products.ToListAsync(ct);

    public async Task<Product> GetByIdAsync(Guid id, CancellationToken ct) =>
        await _db.Products.FirstAsync(p => p.Id == id, ct);

    public async Task UpdateAsync(Product product, CancellationToken ct)
    {
        _db.Products.Update(product);
        await _db.SaveChangesAsync(ct);

        // Notify the system of the change (Essential for Phase 4)
        await _producer.PublishAsync("affiliate.products.updated", product);
    }
}