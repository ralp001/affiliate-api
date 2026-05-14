namespace Affiliate.Application.Abstractions;

public interface IMessageProducer
{
    Task PublishAsync<T>(string topic, T @event) where T : class;
}