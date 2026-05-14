using AffiliateMarketing.Application.Features.Affiliates.Commands;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Swashbuckle.AspNetCore.Annotations;
namespace AffiliateMarketing.API.Controllers;

[ApiController]
[Route("affiliate/api/v1/users")]
[Tags("01. Onboarding & Identity Sync")]
public class UserProvisioningController : ControllerBase
{
    private readonly IMediator _mediator;

    public UserProvisioningController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("sync")]
    public async Task<IActionResult> ProvisionUser([FromBody] RegisterAffiliateCommand command, CancellationToken ct)
    {
        // 1. We receive the data from the External Auth API
        // 2. We send it straight to the Application Layer Handler we built
        var userId = await _mediator.Send(command, ct);

        // 3. Return a 201 Created status
        return CreatedAtAction(nameof(ProvisionUser), new { id = userId }, userId);
    }
}