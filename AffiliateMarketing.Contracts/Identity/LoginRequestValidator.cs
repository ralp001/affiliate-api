using FluentValidation;

namespace AffiliateMarketing.Contracts.Identity
{
    public sealed class LoginRequestValidator
        : AbstractValidator<LoginRequest>
    {
        public LoginRequestValidator()
        {
            RuleFor(x => x.Username).NotEmpty();
            RuleFor(x => x.Password).NotEmpty();
        }
    }
}
