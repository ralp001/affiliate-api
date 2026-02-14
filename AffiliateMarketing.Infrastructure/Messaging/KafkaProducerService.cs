using Confluent.Kafka;
using Newtonsoft.Json;
using Microsoft.Extensions.Configuration;
using Affiliate.Application.Abstractions;

namespace Affiliate.Infrastructure.Messaging;

public class KafkaProducerService : IMessageProducer
{
    private readonly ProducerConfig _config;

    public KafkaProducerService(IConfiguration configuration)
    {
        _config = new ProducerConfig
        {
            // Now pulling Chibuikem's IP from the Environment Variable
            BootstrapServers = configuration["KAFKA_BOOTSTRAP_SERVERS"] ?? "34.70.122.249:9092",
            Acks = Acks.All,
            SocketTimeoutMs = 5000
        };
    }

    public async Task PublishAsync<T>(string topic, T @event) where T : class
    {
        try
        {
            // Building producer with the dynamic config
            using var producer = new ProducerBuilder<string, string>(_config).Build();
            var value = JsonConvert.SerializeObject(@event);

            await producer.ProduceAsync(topic, new Message<string, string>
            {
                Key = Guid.NewGuid().ToString(),
                Value = value
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"KAFKA ERROR: {ex.Message}");
            throw;
        }
    }
}