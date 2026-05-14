using AffiliateMarketing.Application.Features.Dashboard.Queries;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers;

[ApiController]
[Route("api/dashboard")]
[Tags("05. Admin Dashboard")]
public class DashboardController : ControllerBase
{
    private readonly IMediator _mediator;

    public DashboardController(IMediator mediator) => _mediator = mediator;

    /// <summary>
    /// Returns the global analytics for the Affiliate System.
    /// Fulfills requirement: Top Product, Top Country, and Revenue.
    /// </summary>
    [HttpGet("summary")]
    public async Task<IActionResult> GetSummary(CancellationToken ct)
    {
        var result = await _mediator.Send(new GetDashboardSummaryQuery(), ct);
        return Ok(result);
    }
}