using AffiliateMarketing.Application.Common.Security;
using MediatR;

namespace AffiliateMarketing.Application.Common.Behaviours;

public class UserProjectionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> where TRequest : IRequest, new()
{
    private readonly IUserProjectionService _projectionService;

    public UserProjectionBehavior(IUserProjectionService projectionService)
    {
        _projectionService = projectionService;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        await _projectionService.SyncExternalUserAsync(cancellationToken);

        return await next();
    }
}