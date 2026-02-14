using Affiliate.Events;
using AffiliateMarketing.Domain.Enums;
using AffiliateMarketing.Infrastructure.Data;
using Confluent.Kafka;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace AffiliateMarketing.Infrastructure.Messaging;

public class IdentitySyncConsumer : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ConsumerConfig _config;
    private readonly string _topic;

    public IdentitySyncConsumer(IServiceProvider serviceProvider, IConfiguration configuration)
    {
        _serviceProvider = serviceProvider;

        // Use Chibuikem's Broker IP from .env
        _config = new ConsumerConfig
        {
            BootstrapServers = configuration["KAFKA_BOOTSTRAP_SERVERS"] ?? "34.70.122.249:9092",
            GroupId = configuration["KAFKA_GROUP_ID"] ?? "affiliate-identity-sync",
            AutoOffsetReset = AutoOffsetReset.Earliest
        };
        _topic = configuration["KAFKA_USER_EVENTS_TOPIC"] ?? "identity.permissions.changed";
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var consumer = new ConsumerBuilder<string, string>(_config).Build();
        consumer.Subscribe(_topic);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = consumer.Consume(stoppingToken);
                var @event = JsonConvert.DeserializeObject<UserPermissionUpdatedEvent>(result.Message.Value);

                if (@event != null)
                {
                    using var scope = _serviceProvider.CreateScope();
                    var dbContext = scope.ServiceProvider.GetRequiredService<AffiliateDbContext>();

                    var user = await dbContext.Users.FirstOrDefaultAsync(u => u.Id == @event.UserId, stoppingToken);

                    if (user != null)
                    {
                        if (Enum.TryParse<UserRole>(@event.NewRole, true, out var parsedRole))
                        {
                            user.Role = parsedRole.ToString();
                        }
                        else
                        {
                            user.Role = UserRole.Customer.ToString();
                        }
                        await dbContext.SaveChangesAsync(stoppingToken);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Affiliate Kafka Error]: {ex.Message}");
            }
        }
    }
}