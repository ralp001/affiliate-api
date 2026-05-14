using Affiliate.Events;
using Affiliate.Application.Abstractions; // Added for the Interface
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Infrastructure.Services;
using MediatR;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using StackExchange.Redis;
using System.Collections.Generic;

namespace AffiliateMarketing.Infrastructure.Messaging.Services;

public class SchemaRegistryBackgroundService : BackgroundService
{
    private readonly IMediator _mediator;
    private readonly ILogger<SchemaRegistryBackgroundService> _logger;
    private readonly IConnectionMultiplexer _redis;           // Standardized naming with underscore
    private readonly ISchemaDiscoveryService _discoveryService; // Use Interface here!

    public SchemaRegistryBackgroundService(
        IMediator mediator,
        ILogger<SchemaRegistryBackgroundService> logger,
        IConnectionMultiplexer redis,
        ISchemaDiscoveryService discoveryService) // Changed to ISchemaDiscoveryService
    {
        _mediator = mediator;
        _logger = logger;
        _redis = redis;             // Corrected field assignment
        _discoveryService = discoveryService; // Corrected field assignment
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // 1. Startup delay - crucial for VM stability so it doesn't race against Redis
        _logger.LogInformation("🚀 Affiliate Schema Discovery Service is waiting for infrastructure...");
        await Task.Delay(15000, stoppingToken);

        if (stoppingToken.IsCancellationRequested) return;

        try
        {
            var db = _redis.GetDatabase();
            // This matches the "Success Blueprint" Redis key pattern
            string redisKey = "data_type_hash:affiliate-marketing-api";

            // 2. DYNAMIC DISCOVERY - Your 6 Affiliate Entities
            var entitiesToInspect = new List<Type>
            {
                typeof(AffiliateProfile),
                typeof(ClickEvent),
                typeof(Conversion),
                typeof(Product),
                typeof(ReferralLink),
                typeof(User)
            };

            _logger.LogInformation("--> [Discovery] Inspecting {Count} entities for Affiliate API...", entitiesToInspect.Count);

            // Map C# types to the schema format
            var (tables, currentHash) = _discoveryService.DiscoverSchema(entitiesToInspect);

            // 3. CHANGE DETECTION (Redis check)
            string? existingHash = await db.StringGetAsync(redisKey);

            if (existingHash == currentHash)
            {
                _logger.LogInformation("✅ Affiliate Schema is already up to date in Redis.");
                return;
            }

            _logger.LogInformation("--> [Discovery] New schema detected for Affiliate. Emitting to Kafka...");

            // 4. PREPARE THE EVENT
            var schemaEvent = new SchemaDiscoveryEvent
            {
                api_name = "affiliate-marketing-api",
                tables = tables,
                hash = currentHash,
                timestamp = DateTime.UtcNow.ToString("o")
            };

            // 5. PUBLISH & UPDATE STATE
            await _mediator.Publish(schemaEvent, stoppingToken);
            await db.StringSetAsync(redisKey, currentHash);

            _logger.LogInformation("📡 NEW Affiliate Marketing Schema emitted to Kafka. Hash updated in Redis.");
        }
        catch (RedisConnectionException ex)
        {
            _logger.LogError("🛑 [Discovery] Redis Connection Failed for Affiliate. Error: {Msg}", ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError("🛑 [Discovery] Affiliate Background Service error: {Msg}", ex.Message);
        }
    }
}