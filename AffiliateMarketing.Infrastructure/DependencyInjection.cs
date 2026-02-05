using AffiliateMarketing.Application.Identity;
using AffiliateMarketing.Application.Products;
using AffiliateMarketing.Application.Tracking;
using AffiliateMarketing.Infrastructure.Data;
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
            options.UseSqlServer(
            configuration.GetConnectionString("AffiliateMarketingDb")));

            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IProductRepository, ProductRepository>();
            services.AddScoped<ITrackingRepository, TrackingRepository>();

            return services;
        }
    }
}
