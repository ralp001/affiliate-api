using AffiliateMarketing.Application.Common.Security;
using AffiliateMarketing.Infrastructure.Messaging.Models;
using Confluent.Kafka;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace AffiliateMarketing.Infrastructure.BackgroundServices;

public class PermissionConsumer : BackgroundService
{
    private readonly ILogger<PermissionConsumer> _logger;
    private readonly IPermissionCache _cache;

    public PermissionConsumer(
        ILogger<PermissionConsumer> logger,
        IPermissionCache cache)
    {
        _logger = logger;
        _cache = cache;
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var bootstrapServers = Environment.GetEnvironmentVariable("KAFKA_BOOTSTRAP_SERVERS")
            ?? throw new Exception("KAFKA_BOOTSTRAP_SERVERS is not set");

        var config = new ConsumerConfig
        {
            BootstrapServers = bootstrapServers,
            GroupId = "affiliate-permission-consumer",
            AutoOffsetReset = AutoOffsetReset.Earliest
        };

        using var consumer = new ConsumerBuilder<Ignore, string>(config).Build();

        consumer.Subscribe("affiliate-api-permissions");

        _logger.LogInformation("PermissionConsumer started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = consumer.Consume(stoppingToken);

                var message = result.Message.Value;

                var eventData = JsonConvert.DeserializeObject<PermissionEvent>(message);

                if (eventData is null)
                    continue;

                HandleEvent(eventData);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error consuming permission event");
            }
        }

        return Task.CompletedTask;
    }

    private void HandleEvent(PermissionEvent evt)
    {
        switch (evt.EventType)
        {
            case "permission_update":
                HandleSingle(evt);
                break;

            case "bulk_permission_update":
                HandleBulk(evt);
                break;

            case "clearance_type_permission_update":
                HandleClearanceType(evt);
                break;
        }
    }

    private void HandleSingle(PermissionEvent evt)
    {
        if (evt.DataField == null)
            return;

        _cache.SetPermissions(
            evt.ClearanceType,
            evt.ClearanceLevel,
            evt.DataField.FieldPath,
            evt.DataField.Permissions
        );
    }

    private void HandleBulk(PermissionEvent evt)
    {
        if (evt.DataFields == null)
            return;

        foreach (var field in evt.DataFields)
        {
            _cache.SetPermissions(
                evt.ClearanceType,
                evt.ClearanceLevel,
                field.FieldPath,
                field.Permissions
            );
        }
    }

    private void HandleClearanceType(PermissionEvent evt)
    {
        if (evt.ClearanceLevels == null)
            return;

        foreach (var level in evt.ClearanceLevels)
        {
            foreach (var field in level.DataFields)
            {
                _cache.SetPermissions(
                    evt.ClearanceType,
                    level.LevelName,
                    field.FieldPath,
                    field.Permissions
                );
            }
        }
    }
}