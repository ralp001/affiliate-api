using FluentValidation;

namespace AffiliateMarketing.Contracts.Products
{
    public sealed class CreateProductRequestValidator
        : AbstractValidator<CreateProductRequest>
    {
        public CreateProductRequestValidator()
        {
            RuleFor(x => x.Name)
                .NotEmpty()
                .MaximumLength(100);
        }
    }
}
