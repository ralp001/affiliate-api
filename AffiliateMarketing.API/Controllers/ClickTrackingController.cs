using AffiliateMarketing.Application.Features.Tracking.Commands;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers;

[ApiController]
[Route("api/v1/r")]
[Tags("04. Public Tracking")]
public class ClickTrackingController : ControllerBase
{
    private readonly IMediator _mediator;

    public ClickTrackingController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("{code}")]
    public async Task<IActionResult> RedirectAndTrack(string code, CancellationToken ct)
    {
        // 1. Capture Raw Metadata (Superior Quality: Checking for Proxy Headers)
        var ipAddress = Request.Headers["X-Forwarded-For"].FirstOrDefault()
                        ?? HttpContext.Connection.RemoteIpAddress?.ToString()
                        ?? "Unknown";

        var userAgent = Request.Headers["User-Agent"].ToString();

        // Antigravity Tip: Use 'null' if platform is missing so the DB shows "Direct" or "Organic"
        var platform = Request.Query["utm_source"].ToString();

        // 2. Send the Command
        var command = new RecordClickCommand(
            ReferralCode: code,
            IpAddress: ipAddress,
            UserAgent: userAgent,
            Platform: string.IsNullOrEmpty(platform) ? "Organic" : platform
        );

        var targetUrl = await _mediator.Send(command, ct);

        // 3. Fallback Protection
        if (string.IsNullOrEmpty(targetUrl))
        {
            // Boss Requirement: Ensure the user never sees a 404 error
            return Redirect("https://emutare.com");
        }

        return Redirect(targetUrl);
    }
}
