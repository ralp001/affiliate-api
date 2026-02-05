using FluentValidation;

namespace AffiliateMarketing.Contracts.Products
{
    public sealed class SetCommissionRequestValidator
        : AbstractValidator<SetCommissionRequest>
    {
        public SetCommissionRequestValidator()
        {
            RuleFor(x => x.Type)
                .Must(x => x == "percentage" || x == "fixed");

            RuleFor(x => x.Value)
                .GreaterThanOrEqualTo(0);
        }
    }
}
