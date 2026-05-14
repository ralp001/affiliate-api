using AffiliateMarketing.Application.Common.Behaviours;
using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Infrastructure;
using AffiliateMarketing.Infrastructure.Data;
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi;
using StackExchange.Redis;
using System.Text.Json;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// --- STEP 1: LOAD ENVIRONMENT VARIABLES ---
DotNetEnv.Env.Load();
builder.Configuration.AddEnvironmentVariables();

// --- STEP 2: REDIS INITIALIZATION ---
var rawRedisUrl = Environment.GetEnvironmentVariable("REDIS_CONNECTION");
string redisUrl;
if (!string.IsNullOrEmpty(rawRedisUrl) && rawRedisUrl.StartsWith("redis://"))
{
    var uri = new Uri(rawRedisUrl);
    var password = uri.UserInfo.Split(':').LastOrDefault();
    redisUrl = $"{uri.Host}:{uri.Port},password={password},abortConnect=false";
}
else
{
    redisUrl = rawRedisUrl ?? "34.70.122.249:6379,abortConnect=false";
}

try
{
    var multiplexer = ConnectionMultiplexer.Connect(redisUrl);
    builder.Services.AddSingleton<IConnectionMultiplexer>(multiplexer);
    Console.WriteLine("✅ Redis IConnectionMultiplexer initialized for Affiliate.");
}
catch (Exception ex)
{
    Console.WriteLine($"🛑 Redis Connection Error: {ex.Message}");
}

// --- STEP 3: CORE SERVICES ---
builder.Services.AddControllers().AddJsonOptions(options =>
{
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
});


builder.Services.AddEndpointsApiExplorer();
builder.Services.AddProblemDetails();

// --- STEP 4: INFRASTRUCTURE & MESSAGING ---
builder.Services.AddInfrastructure(builder.Configuration);

// FIX: Map the Interface to the Implementation so Handlers can inject IAffiliateDbContext
// --- STEP 4.1: MEDIATR (Stays here because it bridges projects) ---
builder.Services.AddMediatR(cfg =>
{
    cfg.RegisterServicesFromAssembly(typeof(Program).Assembly);
    cfg.RegisterServicesFromAssembly(typeof(IAffiliateDbContext).Assembly);
});

builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(UserProjectionBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(AuthorizationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(PermissionBehavior<,>));
// --- STEP 5: SWAGGER ---
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Emutare Affiliate API", Version = "v1" });
    /*c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme.",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });*/
});

// --- STEP 6: AUTHENTICATION ---
/*builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        var jwtKey = builder.Configuration["JWT_SECRET_KEY"];
        if (string.IsNullOrEmpty(jwtKey))
        {
            jwtKey = "Temporary_Local_Development_Key_32_Chars_Long!!";
            Console.WriteLine("⚠️ Warning: Using dummy JWT key for local development.");
        }

        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = "Emutare Auth",
            ValidAudience = "http://localhost:8000",
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey)),
            ClockSkew = TimeSpan.Zero
        };
    });*/

var app = builder.Build();

// --- STEP 7: MIGRATIONS ---
using (var scope = app.Services.CreateScope())
{
    try
    {
        scope.ServiceProvider.GetRequiredService<AffiliateDbContext>().Database.Migrate();
        Console.WriteLine("✅ Affiliate database migration applied.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"🛑 Migration Error: {ex.Message}");
    }
}

// --- STEP 8: PIPELINE (Fixed for Nginx) ---
app.UsePathBase("/affiliate");
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/affiliate/swagger/v1/swagger.json", "Affiliate API V1");
    c.RoutePrefix = "swagger";
});

app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();