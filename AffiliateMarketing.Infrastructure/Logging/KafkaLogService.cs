using AffiliateMarketing.Application.Abstractions;
using Confluent.Kafka;
using Newtonsoft.Json;
using Microsoft.Extensions.Configuration;

namespace AffiliateMarketing.Infrastructure.Logging;

public class KafkaLogService : ILogService
{
    private readonly IProducer<string, string> _producer;
    private readonly string _topic;

    public KafkaLogService(IConfiguration configuration)
    {
        // Pulling from .env/Configuration instead of hardcoded 10.128.0.3
        var bootstrapServers = configuration["KAFKA_BOOTSTRAP_SERVERS"] ?? "34.70.122.249:9092";
        _topic = configuration["KAFKA_AUDIT_LOGS_TOPIC"] ?? "system.logs";

        var config = new ProducerConfig { BootstrapServers = bootstrapServers };
        _producer = new ProducerBuilder<string, string>(config).Build();
    }

    public async Task LogAsync(Guid? userId, string action, string status, string message = "")
    {
        var logEntry = new
        {
            Api = "Affiliate",
            UserId = userId,
            Action = action,
            Status = status,
            Message = message,
            Timestamp = DateTime.UtcNow
        };

        await _producer.ProduceAsync(_topic, new Message<string, string>
        {
            Value = JsonConvert.SerializeObject(logEntry)
        });
    }
}