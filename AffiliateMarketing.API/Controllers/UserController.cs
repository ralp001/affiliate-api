using AffiliateMarketing.Application.Identity.Commands;
using AffiliateMarketing.Contracts.Identity;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers
{
    [ApiController]
    [Route("users")]
    public sealed class UsersController : ControllerBase
    {
        private readonly IMediator _mediator;

        public UsersController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register(RegisterUserRequest request)
        {
            try
            {
                await _mediator.Send(new RegisterUserCommand(
                    request.Username,
                    request.Email,
                    request.Password));

                return Ok();
            }
            catch (InvalidOperationException ex)
            {
                return BadRequest(new { message = ex.Message });
            }
        }

    }
}
