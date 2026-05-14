using Affiliate.Events;
using AffiliateMarketing.Infrastructure.Data;
using Confluent.Kafka;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

public class IdentitySyncConsumer : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<IdentitySyncConsumer> _logger;
    private readonly ConsumerConfig _config;
    private readonly string _topic;

    public IdentitySyncConsumer(
        IServiceProvider serviceProvider,
        IConfiguration configuration,
        ILogger<IdentitySyncConsumer> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;

        // 1. MATCH PRODUCT PATTERN: Check Environment Variables first for the Topic
        _topic = Environment.GetEnvironmentVariable("KAFKA_USER_EVENTS_TOPIC")
                 ?? configuration["KAFKA_USER_EVENTS_TOPIC"]
                 ?? "identity.permissions.changed";

        // 2. MATCH PRODUCT PATTERN: Use Environment Variables for the Broker and GroupId
        _config = new ConsumerConfig
        {
            BootstrapServers = Environment.GetEnvironmentVariable("KAFKA_BOOTSTRAP_SERVERS")
                               ?? configuration["KAFKA_BOOTSTRAP_SERVERS"]
                               ?? "34.70.122.249:9092",

            GroupId = Environment.GetEnvironmentVariable("KAFKA_GROUP_ID")
                      ?? "affiliate-identity-sync-group",

            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = true,
            // Added for better stability in background tasks
            SocketTimeoutMs = 60000,
            SessionTimeoutMs = 30000
        };
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // 3. STARTUP DELAY: Allow Infrastructure to warm up
        await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);

        using var consumer = new ConsumerBuilder<string, string>(_config).Build();
        consumer.Subscribe(_topic);

        _logger.LogInformation("📡 Affiliate Identity Sync Consumer started. Listening on topic: {Topic}", _topic);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = consumer.Consume(stoppingToken);
                if (result?.Message?.Value == null) continue;

                var @event = JsonConvert.DeserializeObject<UserPermissionUpdatedEvent>(result.Message.Value);

                if (@event != null)
                {
                    using var scope = _serviceProvider.CreateScope();
                    var db = scope.ServiceProvider.GetRequiredService<AffiliateDbContext>();

                    var localCache = await db.UserClearances
                        .FirstOrDefaultAsync(u => u.UserId == @event.UserId, stoppingToken);

                    if (localCache != null)
                    {
                        localCache.Role = @event.NewRole;
                        localCache.LastUpdated = DateTime.UtcNow;
                        _logger.LogInformation("✅ Updated permissions for User {UserId} in Affiliate DB.", @event.UserId);
                    }
                    else
                    {
                        db.UserClearances.Add(new UserClearance
                        {
                            UserId = @event.UserId,
                            Role = @event.NewRole,
                            LastUpdated = DateTime.UtcNow
                        });
                        _logger.LogInformation("📝 Created new permission entry for User {UserId} in Affiliate DB.", @event.UserId);
                    }

                    await db.SaveChangesAsync(stoppingToken);
                }
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError("🛑 Affiliate Identity Sync Consumer Error: {Message}", ex.Message);
                await Task.Delay(10000, stoppingToken); // Match Product: 10s wait on error
            }
        }

        consumer.Close();
    }
}