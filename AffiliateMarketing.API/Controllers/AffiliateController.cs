using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Contracts.Affiliate;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers
{
    [ApiController]
    [Route("affiliate")]
    public sealed class AffiliateController : ControllerBase
    {
        private readonly IProductRepository _productRepository;
        private readonly ITrackingRepository _trackingRepository;

        public AffiliateController(
            IProductRepository productRepository,
            ITrackingRepository trackingRepository)
        {
            _productRepository = productRepository;
            _trackingRepository = trackingRepository;
        }

        [HttpGet("products")]
        public async Task<IActionResult> GetProducts(
            CancellationToken cancellationToken)
        {
            var products = await _productRepository
                .GetAllAsync(cancellationToken);

            return Ok(products.Select(p => new AffiliateProductResponse
            {
                ProductName = p.Name,
                CommissionType = p.CommissionType,
                CommissionValue = p.CommissionValue
            }));
        }

        [HttpGet("resources")]
        public IActionResult GetResources()
        {
            return Ok(new[]
            {
                new {
                    name = "Product Banner",
                    url = "https://cdn.example.com/banner.png"
                }
            });
        }

        [HttpGet("dashboard/metrics")]
        public async Task<IActionResult> GetMetrics(
    [FromQuery] string trackingId,
    CancellationToken cancellationToken)
        {
            var clicks = await _trackingRepository
                .GetClickCountAsync(trackingId, cancellationToken);

            return Ok(new AffiliateMetricsResponse
            {
                TotalClicks = clicks
            });
        }
    }
}


    

