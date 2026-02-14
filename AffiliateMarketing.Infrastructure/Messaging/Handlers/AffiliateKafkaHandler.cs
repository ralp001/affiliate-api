using MediatR;
using Affiliate.Application.Abstractions;
using Affiliate.Events;

namespace Affiliate.Infrastructure.Messaging.Handlers;

public class AffiliateKafkaHandler :
    INotificationHandler<AffiliateRegisteredEvent>,
    INotificationHandler<CommissionUpdatedEvent>
{
    private readonly IMessageProducer _producer;

    public AffiliateKafkaHandler(IMessageProducer producer)
    {
        _producer = producer;
    }

    public async Task Handle(AffiliateRegisteredEvent notification, CancellationToken ct)
    {
        await _producer.PublishAsync("affiliate.registered", notification);
    }

    public async Task Handle(CommissionUpdatedEvent notification, CancellationToken ct)
    {
        await _producer.PublishAsync("affiliate.commissions", notification);
    }
}