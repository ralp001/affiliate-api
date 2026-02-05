using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Contracts.Identity;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers
{
    [ApiController]
    [Route("auth")]
    public sealed class AuthController : ControllerBase
    {
        private readonly IUserRepository _userRepository;

        public AuthController(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(LoginRequest request,
            CancellationToken cancellationToken)
        {
            var user = await _userRepository
                .GetByUsernameAsync(request.Username, cancellationToken);

            if (user == null ||
                !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            {
                return Unauthorized("Invalid credentials");
            }

            return Ok(new { message = "Login successful" });
        }
    }
}
