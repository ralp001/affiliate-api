using AffiliateMarketing.Infrastructure;
using AffiliateMarketing.Infrastructure.Data;
using FluentValidation;
using FluentValidation.AspNetCore;
using MediatR;
using Microsoft.AspNetCore.HttpOverrides; // Added for Nginx
using Microsoft.EntityFrameworkCore;    // Added for Migration

var builder = WebApplication.CreateBuilder(args);

// --------------------
// Service Registration
// --------------------
builder.Services.AddControllers();
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddFluentValidationClientsideAdapters();
DotNetEnv.Env.Load();
builder.Configuration.AddEnvironmentVariables();

builder.Services.AddValidatorsFromAssemblyContaining<AffiliateMarketing.Contracts.Identity.RegisterUserRequestValidator>();

builder.Services.AddMediatR(cfg =>
    cfg.RegisterServicesFromAssemblyContaining<AffiliateMarketing.Application.Identity.Commands.RegisterUserCommand>());

builder.Services.AddInfrastructure(builder.Configuration);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options => {
    options.AddDefaultPolicy(policy => {
        policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod();
    });
});

var app = builder.Build();

// --------------------
// NEW: Auto-Migrate Database on Startup
// --------------------
using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    try
    {
        var context = services.GetRequiredService<AffiliateDbContext>();
        context.Database.Migrate();
    }
    catch (Exception ex)
    {
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "An error occurred while migrating the database.");
    }
}

// --------------------
// HTTP pipeline
// --------------------

// Required for Nginx reverse proxy to pass headers correctly
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto
});

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();

// Note: If you have Nginx handling SSL, you might want to comment out HttpsRedirection 
// to avoid redirect loops, but keeping it is usually fine.
//app.UseHttpsRedirection();

app.UseAuthorization();
app.MapControllers();

app.Run();