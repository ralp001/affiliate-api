using FluentValidation;

namespace AffiliateMarketing.Contracts.Identity
{
    public sealed class RegisterUserRequestValidator
        : AbstractValidator<RegisterUserRequest>
    {
        public RegisterUserRequestValidator()
        {
            RuleFor(x => x.Username)
                .NotEmpty()
                .MinimumLength(3)
                .MaximumLength(50);

            RuleFor(x => x.Password)
                .NotEmpty()
                .MinimumLength(8)
                .MaximumLength(100);
            RuleFor(x => x.Email)
    .NotEmpty()
    .EmailAddress();
        }
    }
}
