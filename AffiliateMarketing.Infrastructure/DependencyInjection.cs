using Affiliate.Application.Abstractions;
using Affiliate.Infrastructure.Messaging;
using AffiliateMarketing.Application.Abstractions;
using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Infrastructure.Data;
using AffiliateMarketing.Infrastructure.Logging;
using AffiliateMarketing.Infrastructure.Messaging;
using AffiliateMarketing.Infrastructure.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace AffiliateMarketing.Infrastructure
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructure(
            this IServiceCollection services,
            IConfiguration configuration)
        {
            services.AddDbContext<AffiliateDbContext>(options =>
            options.UseNpgsql(
            configuration.GetConnectionString("AffiliateMarketingDb")));

            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IProductRepository, ProductRepository>();
            services.AddScoped<ITrackingRepository, TrackingRepository>();
            services.AddSingleton<IMessageProducer, KafkaProducerService>();
            services.AddSingleton<ILogService, KafkaLogService>();
            services.AddHostedService<IdentitySyncConsumer>();

            return services;
        }
    }
}
