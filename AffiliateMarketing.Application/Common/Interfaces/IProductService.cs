namespace AffiliateMarketing.Application.Common.Interfaces;

public interface IProductService
{
    // Fetches the latest price/details from the Billing/Payment API
    // to ensure the 60% commission is calculated on real-time data.
    Task<decimal> GetProductPriceAsync(Guid productId);
    Task<bool> IsProductActiveAsync(Guid productId);
}