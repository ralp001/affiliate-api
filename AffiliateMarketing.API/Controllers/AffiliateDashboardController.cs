using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Application.Abstractions;
using AffiliateMarketing.Application.Features.Dashboard.Queries;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace AffiliateMarketing.API.Controllers;

// [Authorize] // Temporarily commented out for Phase 1 Demo
[ApiController]
[Route("affiliate/api/v1/dashboard")]
[Tags("02. Affiliate Performance Dashboard")]
public class AffiliateDashboardController : ControllerBase
{
    private readonly ICurrentUserService _currentUserService;
    private readonly ILogService _logService;
    private readonly IMediator _mediator;

    public AffiliateDashboardController(
        ICurrentUserService currentUserService,
        ILogService logService,
        IMediator mediator)
    {
        _currentUserService = currentUserService;
        _logService = logService;
        _mediator = mediator;
    }

    /// <summary>
    /// Returns the comprehensive dashboard summary including top products, affiliates, and geographic insights.
    /// </summary>
    [HttpGet("summary")]
    public async Task<IActionResult> GetSummary(CancellationToken ct)
    {
        var userId = _currentUserService.UserId;

        // BOSS REQUIREMENT: Log every dashboard access for security audits
        await _logService.LogAsync(userId, "View_Dashboard", "Success", "User viewed performance stats.");

        // SENIOR ARCHITECTURE: Using MediatR to call our complex data handler
        var result = await _mediator.Send(new GetDashboardSummaryQuery(), ct);

        return Ok(result);
    }

    /// <summary>
    /// Phase 2: Temporary endpoint to simulate a sale for the demo video.
    /// This allows you to show revenue increasing in real-time.
    /// </summary>
    [HttpPost("simulate-sale")]
    public async Task<IActionResult> SimulateSale([FromBody] AffiliateMarketing.Application.Features.Dashboard.Commands.SimulateSaleCommand command)
    {
        var result = await _mediator.Send(command);
        return result
            ? Ok(new { Message = "Sale Simulated Successfully. Refresh dashboard to see updates." })
            : BadRequest("Invalid Referral Code or Product ID.");
    }
}