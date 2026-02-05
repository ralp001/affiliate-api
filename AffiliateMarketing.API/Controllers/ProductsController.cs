using AffiliateMarketing.Application.Products.Commands;
using AffiliateMarketing.Contracts.Products;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace AffiliateMarketing.API.Controllers
{
    [ApiController]
    [Route("products")]
    public sealed class ProductsController : ControllerBase
    {
        private readonly IMediator _mediator;

        public ProductsController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost("create")]
        public async Task<IActionResult> CreateProduct(
            [FromBody] CreateProductRequest request,
            CancellationToken cancellationToken)
        {
            await _mediator.Send(
                new CreateProductCommand(request.Name),
                cancellationToken);

            return Created("", new { message = "Product created" });
        }

        [HttpPost("{id}/commission")]
        public async Task<IActionResult> SetCommission(
    Guid id,
    SetCommissionRequest request,
    CancellationToken cancellationToken)
        {
            await _mediator.Send(
                new SetCommissionCommand(id, request.Type, request.Value),
                cancellationToken);

            return Ok(new { message = "Commission set" });
        }

    }
}
