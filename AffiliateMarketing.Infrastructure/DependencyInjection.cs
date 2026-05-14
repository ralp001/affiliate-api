using AffiliateMarketing.Application.Common.Security;
using AffiliateMarketing.Infrastructure.BackgroundServices;
using AffiliateMarketing.Infrastructure.Security;
using AffiliateMarketing.Infrastructure.Security.Jwt;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using Ticketing.Infrastructure.Security;

namespace AffiliateMarketing.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        var jwtOptions = new JwtOptions
        {
            InternalSecret = configuration["INTERNAL_AUTH_JWT_SECRET"]!,
            ExternalSecret = configuration["EXTERNAL_AUTH_JWT_SECRET"]!,
            Algorithm = configuration["JWT_ALGORITHM"] ?? "HS256"
        };

        services.AddSingleton(jwtOptions);

        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.Events = new MultiTenantJwtBearerEvents(jwtOptions);

                options.RequireHttpsMetadata = false;
                options.SaveToken = true;

                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = false,
                    ValidateAudience = false,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = false
                };
            });

        services.AddAuthorization();

        services.AddHttpContextAccessor();
        services.AddScoped<ICurrentUserService, CurrentUserService>();

        services.AddSingleton<IPermissionCache, PermissionCache>();
        services.AddScoped<IPermissionService, PermissionService>();
        services.AddScoped<IUserProjectionService, UserProjectionService>();

        services.AddHostedService<PermissionConsumer>();

        return services;
    }
}