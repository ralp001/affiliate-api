using AffiliateMarketing.Application.Common.Interfaces;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers;

//[Authorize]
[ApiController]
[Route("affiliate/api/v1/links")]
[Tags("03. Referral Engine")]
public class ReferralLinksController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly ICurrentUserService _currentUser;

    public ReferralLinksController(IMediator mediator, ICurrentUserService currentUser)
    {
        _mediator = mediator;
        _currentUser = currentUser;
    }

    /// <summary>
    /// Generates a unique referral link for a specific product.
    /// </summary>
    [HttpPost("generate")]
    public async Task<IActionResult> Generate([FromBody] GenerateLinkRequest request, CancellationToken ct)
    {
        // 1. Create the command using the logged-in user's ID
        var command = new GenerateLinkCommand(
        _currentUser.UserId ?? Guid.Empty, // Maps to AffiliateProfileId
        request.ProductId,
        "Web" // Maps to SourcePlatform (required by your record)
    );

        // 2. This triggers the GenerateLinkHandler
        var result = await _mediator.Send(command, ct);

        return Ok(new { ReferralCode = result });
    }
}

public record GenerateLinkRequest(Guid ProductId);