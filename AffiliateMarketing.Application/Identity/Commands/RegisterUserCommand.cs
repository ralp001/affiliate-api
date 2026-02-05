using MediatR;

namespace AffiliateMarketing.Application.Identity.Commands
{
    public sealed record RegisterUserCommand(
        string Username,
        string Email,
        string Password
    ) : IRequest;
}
