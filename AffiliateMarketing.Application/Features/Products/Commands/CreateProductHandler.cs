using MediatR;
using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Domain.Entities;

namespace AffiliateMarketing.Application.Features.Products.Commands;

public class CreateProductHandler : IRequestHandler<CreateProductCommand, Guid>
{
    private readonly IAffiliateDbContext _context;

    public CreateProductHandler(IAffiliateDbContext context)
    {
        _context = context;
    }

    public async Task<Guid> Handle(CreateProductCommand request, CancellationToken ct)
    {
        var product = new Product
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Description = request.Description,
            CommissionType = request.CommissionType,
            CommissionValue = request.CommissionValue,
            BasePrice = request.BasePrice,
            Currency = request.Currency,
            IsAvailableForAffiliates = true
        };

        _context.Products.Add(product);

        // Log this action for ZAP/Security Audit
        _context.AuditLogs.Add(new AuditLog
        {
            EntityName = "Product",
            Action = "Create",
            NewValues = $"Name: {product.Name}, Commission: {product.CommissionValue}"
        });

        await _context.SaveChangesAsync(ct);
        return product.Id;
    }
}