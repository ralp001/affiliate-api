using Affiliate.Application.Abstractions;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace AffiliateMarketing.Infrastructure.Messaging;

public class KafkaProducer : IMessageProducer, IDisposable
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<KafkaProducer> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public KafkaProducer(IConfiguration configuration, ILogger<KafkaProducer> logger)
    {
        _logger = logger;

        // MATCH PRODUCT PATTERN: Prioritize Environment Variables for the VM
        var bootstrapServers = Environment.GetEnvironmentVariable("KAFKA_BOOTSTRAP_SERVERS")
                               ?? configuration["KAFKA_BOOTSTRAP_SERVERS"]
                               ?? "34.70.122.249:9092";

        var config = new ProducerConfig
        {
            BootstrapServers = bootstrapServers,
            Acks = Acks.All,
            MessageTimeoutMs = 5000,
            RequestTimeoutMs = 5000,
            // Added to handle network flutters on the VM
            SocketTimeoutMs = 60000,
            RetryBackoffMs = 1000
        };

        _producer = new ProducerBuilder<string, string>(config).Build();

        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            WriteIndented = false,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };
        _jsonOptions.Converters.Add(new JsonStringEnumConverter());
    }

    public async Task PublishAsync<T>(string topic, T @event) where T : class
    {
        try
        {
            var payload = JsonSerializer.Serialize(@event, _jsonOptions);

            var result = await _producer.ProduceAsync(topic, new Message<string, string>
            {
                Key = typeof(T).Name,
                Value = payload
            });

            _logger.LogInformation("✅ KAFKA SUCCESS (Affiliate): Delivered to {TopicPartitionOffset}", result.TopicPartitionOffset);
        }
        catch (ProduceException<string, string> ex)
        {
            _logger.LogError("🛑 KAFKA ERROR (Affiliate): {Reason}", ex.Error.Reason);
        }
        catch (Exception ex)
        {
            _logger.LogError("🛑 UNEXPECTED ERROR (Affiliate): {Message}", ex.Message);
        }
    }

    public void Dispose()
    {
        _producer?.Flush(TimeSpan.FromSeconds(10));
        _producer?.Dispose();
    }
}