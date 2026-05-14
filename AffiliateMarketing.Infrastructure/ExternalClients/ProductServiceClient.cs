using AffiliateMarketing.Application.Common.Interfaces;
using Microsoft.Extensions.Configuration;
using System.Net.Http.Json;

namespace AffiliateMarketing.Infrastructure.ExternalClients;

public sealed class ProductServiceClient : IProductService
{
    private readonly HttpClient _httpClient;

    public ProductServiceClient(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _httpClient.BaseAddress = new Uri(configuration["API_MANAGER_URL"] ?? "http://34.70.122.249:5000");
    }

    public async Task<decimal> GetProductPriceAsync(Guid productId)
    {
        // Calling the Billing API through the Manager
        var response = await _httpClient.GetAsync($"/billing-api/products/{productId}/price");
        return response.IsSuccessStatusCode ? await response.Content.ReadFromJsonAsync<decimal>() : 0;
    }

    public async Task<bool> IsProductActiveAsync(Guid productId)
    {
        var response = await _httpClient.GetAsync($"/billing-api/products/{productId}/status");
        return response.IsSuccessStatusCode;
    }
}