using Affiliate.Application.Abstractions;
using AffiliateMarketing.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Newtonsoft.Json;

namespace AffiliateMarketing.Infrastructure.Interceptors;

public sealed class AuditLogInterceptor : SaveChangesInterceptor
{
    private readonly IMessageProducer _producer;

    public AuditLogInterceptor(IMessageProducer producer)
    {
        _producer = producer;
    }

    public override async ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData,
        InterceptionResult<int> result,
        CancellationToken ct = default)
    {
        var context = eventData.Context;
        if (context == null) return result;

        // Capture all changes (Create, Update, Delete)
        var entries = context.ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted)
            .ToList();

        foreach (var entry in entries)
        {
            var oldValues = new Dictionary<string, object?>();
            var newValues = new Dictionary<string, object?>();

            foreach (var prop in entry.Properties)
            {
                if (entry.State == EntityState.Added)
                    newValues[prop.Metadata.Name] = prop.CurrentValue;

                else if (entry.State == EntityState.Deleted)
                    oldValues[prop.Metadata.Name] = prop.OriginalValue;

                else if (entry.State == EntityState.Modified && prop.IsModified)
                {
                    oldValues[prop.Metadata.Name] = prop.OriginalValue;
                    newValues[prop.Metadata.Name] = prop.CurrentValue;
                }
            }

            var auditEntry = new
            {
                Api = "Affiliate_Marketing_API",
                EntityName = entry.Entity.GetType().Name,
                Action = entry.State.ToString(),
                OldValues = oldValues,
                NewValues = newValues,
                Timestamp = DateTime.UtcNow
            };

            // BOSS REQUIREMENT: Fan-out to the central audit topic
            // We use 'affiliate-logs' to match the Unified Logs API requirement
            _ = _producer.PublishAsync("affiliate-logs", auditEntry);
        }

        return await base.SavingChangesAsync(eventData, result, ct);
    }
}