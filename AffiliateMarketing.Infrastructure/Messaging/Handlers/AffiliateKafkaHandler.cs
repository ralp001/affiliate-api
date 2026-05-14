using Affiliate.Application.Abstractions;
using Affiliate.Events;
using MediatR;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

public class AffiliateKafkaHandler :
    INotificationHandler<AffiliateRegisteredEvent>,
    INotificationHandler<CommissionUpdatedEvent>,
    INotificationHandler<SchemaDiscoveryEvent>
{
    private readonly IMessageProducer _producer;
    private readonly ILogger<AffiliateKafkaHandler> _logger;
    private readonly IConfiguration _configuration;

    public AffiliateKafkaHandler(
        IMessageProducer producer,
        ILogger<AffiliateKafkaHandler> logger,
        IConfiguration configuration)
    {
        _producer = producer;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task Handle(AffiliateRegisteredEvent notification, CancellationToken ct)
    {
        // MATCH PRODUCT PATTERN: Check Environment Variables for the topic name
        var topic = Environment.GetEnvironmentVariable("KAFKA_AFFILIATE_TOPIC")
                    ?? _configuration["KAFKA_AFFILIATE_TOPIC"]
                    ?? "user-events";

        await _producer.PublishAsync(topic, notification);
    }

    public async Task Handle(CommissionUpdatedEvent notification, CancellationToken ct)
    {
        var topic = Environment.GetEnvironmentVariable("KAFKA_LOGS_TOPIC")
                    ?? _configuration["KAFKA_LOGS_TOPIC"]
                    ?? "affiliate-logs";

        await _producer.PublishAsync(topic, new
        {
            event_type = "commission_updated",
            source = "affiliate_marketing_api",
            data = notification
        });
    }

    public async Task Handle(SchemaDiscoveryEvent notification, CancellationToken ct)
    {
        // CRITICAL: Ensure this matches the Product/Ticketing topic name in .env
        var topic = Environment.GetEnvironmentVariable("KAFKA_ENROLLMENT_TOPIC")
                    ?? _configuration["KAFKA_ENROLLMENT_TOPIC"]
                    ?? "api-data-types";

        _logger.LogInformation("🚀 EMITTING Schema Discovery for {ApiName} to Kafka topic: {Topic}",
            notification.api_name, topic);

        await _producer.PublishAsync(topic, notification);

        _logger.LogInformation("✅ Schema Discovery event sent successfully for {ApiName}.",
            notification.api_name);
    }
}