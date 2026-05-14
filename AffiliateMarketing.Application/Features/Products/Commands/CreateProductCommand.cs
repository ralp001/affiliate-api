using AffiliateMarketing.Domain.Enums; // Assuming Enum is here or in Enums namespace
using MediatR;

namespace AffiliateMarketing.Application.Features.Products.Commands;

public record CreateProductCommand(
    string Name,
    string Description,
    CommissionType CommissionType,
    decimal CommissionValue,
    decimal BasePrice,
    string Currency = "NGN"
) : IRequest<Guid>;