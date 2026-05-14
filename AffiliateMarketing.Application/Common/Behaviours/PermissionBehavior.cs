using AffiliateMarketing.Application.Common.Security;
using MediatR;

namespace AffiliateMarketing.Application.Common.Behaviours;

public class PermissionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> where TRequest : IRequest, new()
{
    private readonly IPermissionService _permissionService;

    public PermissionBehavior(IPermissionService permissionService)
    {
        _permissionService = permissionService;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        if (request is IRequirePermission permissionRequest)
        {
            var allowed = _permissionService.HasPermission(
                permissionRequest.FieldPath,
                permissionRequest.Action
            );

            if (!allowed)
                throw new UnauthorizedAccessException(
                    $"Permission denied: {permissionRequest.FieldPath}:{permissionRequest.Action}"
                );
        }

        return await next();
    }
}