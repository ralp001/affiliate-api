using AffiliateMarketing.Application.Abstractions;
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
        private readonly ILogService _logService; // New

        public AffiliateController(
            IProductRepository productRepository,
            ITrackingRepository trackingRepository,
            ILogService logService)
        {
            _productRepository = productRepository;
            _trackingRepository = trackingRepository;
            _logService = logService;
        }

        [HttpGet("dashboard/metrics")]
        public async Task<IActionResult> GetMetrics([FromQuery] string trackingId, CancellationToken cancellationToken)
        {
            try
            {
                var clicks = await _trackingRepository.GetClickCountAsync(trackingId, cancellationToken);
                await _logService.LogAsync(null, "ViewMetrics", "Success", $"TrackingId: {trackingId}");

                return Ok(new AffiliateMetricsResponse { TotalClicks = clicks });
            }
            catch (Exception ex)
            {
                await _logService.LogAsync(null, "ViewMetrics", "Error", ex.Message);
                return StatusCode(500);
            }
        }
    }
}





