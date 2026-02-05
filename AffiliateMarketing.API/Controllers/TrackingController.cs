using AffiliateMarketing.Application.Tracking;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers
{
    [ApiController]
    [Route("track")]
    public sealed class TrackingController : ControllerBase
    {
        private readonly ITrackingRepository _trackingRepository;

        public TrackingController(ITrackingRepository trackingRepository)
        {
            _trackingRepository = trackingRepository;
        }

        [HttpGet("click/{trackingId}")]
        public async Task<IActionResult> Track(
            string trackingId,
            CancellationToken cancellationToken)
        {
            var userAgent = Request.Headers.UserAgent.ToString();
            var ip = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown";

            await _trackingRepository.RegisterClickAsync(
                trackingId,
                userAgent,
                ip,
                cancellationToken);

            return Ok(new { message = "Click registered" });
        }
    }
}
