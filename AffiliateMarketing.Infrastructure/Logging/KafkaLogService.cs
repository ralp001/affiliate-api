using Affiliate.Application.Abstractions;
using AffiliateMarketing.Application.Abstractions;
using Confluent.Kafka;
using Newtonsoft.Json;
using Microsoft.Extensions.Configuration;

namespace AffiliateMarketing.Infrastructure.Logging;

public class KafkaLogService : ILogService
{
    private readonly IMessageProducer _producer;
    private readonly string _topic;

    public KafkaLogService(IMessageProducer producer, IConfiguration configuration)
    {
        _producer = producer;
        _topic = configuration["KAFKA_AUDIT_LOGS_TOPIC"] ?? "affiliate-logs";
    }

    public async Task LogAsync(Guid? userId, string action, string status, string message = "")
    {
        var logEntry = new
        {
            Api = "AffiliateMarketing_API",
            UserId = userId,
            Action = action,
            Status = status,
            Message = message,
            Timestamp = DateTime.UtcNow,
            Environment = "Production_VM"
        };

        await _producer.PublishAsync(_topic, logEntry);
    }
}