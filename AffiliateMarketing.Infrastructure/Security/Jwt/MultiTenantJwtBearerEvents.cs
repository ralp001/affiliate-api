using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Text;

namespace AffiliateMarketing.Infrastructure.Security.Jwt;

public class MultiTenantJwtBearerEvents : JwtBearerEvents
{
    private readonly JwtOptions _options;

    public MultiTenantJwtBearerEvents(JwtOptions options)
    {
        _options = options;
    }

    public override Task MessageReceived(MessageReceivedContext context)
    {
        var token = context.Request.Headers["Authorization"]
            .FirstOrDefault()?.Replace("Bearer ", "");

        if (string.IsNullOrEmpty(token))
            return Task.CompletedTask;

        var handler = new JwtSecurityTokenHandler();

        if (!handler.CanReadToken(token))
            return Task.CompletedTask;

        var jwt = handler.ReadJwtToken(token);

        var issuer = jwt.Issuer;

        string? secret = issuer switch
        {
            var i when i == AuthConstants.InternalIssuer => _options.InternalSecret,
            var i when i == AuthConstants.ExternalIssuer => _options.ExternalSecret,
            _ => null
        };

        if (secret is null)
        {
            context.Fail("Invalid issuer");
            return Task.CompletedTask;
        }

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));

        context.Options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = issuer,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = key,
            NameClaimType = "sub",
            RoleClaimType = "responsibility_category"
        };

        return Task.CompletedTask;
    }
}