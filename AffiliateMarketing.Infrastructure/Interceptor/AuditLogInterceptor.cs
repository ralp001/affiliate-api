using Affiliate.Application.Abstractions;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Newtonsoft.Json;

namespace Ticketing.Infrastructure.Interceptors;

public class AuditLogInterceptor : SaveChangesInterceptor
{
    private readonly IMessageProducer _producer;

    public AuditLogInterceptor(IMessageProducer producer) => _producer = producer;

    public override async ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData, InterceptionResult<int> result, CancellationToken ct = default)
    {
        var context = eventData.Context;
        if (context == null) return result;

        var entries = context.ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted)
            .ToList();

        foreach (var entry in entries)
        {
            var oldValues = new Dictionary<string, object?>();
            var newValues = new Dictionary<string, object?>();

            foreach (var prop in entry.Properties)
            {
                if (entry.State == EntityState.Added) newValues[prop.Metadata.Name] = prop.CurrentValue;
                else if (entry.State == EntityState.Deleted) oldValues[prop.Metadata.Name] = prop.OriginalValue;
                else if (entry.State == EntityState.Modified && prop.IsModified)
                {
                    oldValues[prop.Metadata.Name] = prop.OriginalValue;
                    newValues[prop.Metadata.Name] = prop.CurrentValue;
                }
            }

            var audit = new AuditLog
            {
                EntityName = entry.Entity.GetType().Name,
                Action = entry.State.ToString(),
                OldValues = JsonConvert.SerializeObject(oldValues),
                NewValues = JsonConvert.SerializeObject(newValues)
            };

            // Send to the central audit topic on the remote VM
            _ = _producer.PublishAsync("Affiliate.audit.logs", audit);
        }
        return await base.SavingChangesAsync(eventData, result, ct);
    }
}