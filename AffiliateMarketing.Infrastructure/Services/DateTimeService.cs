using AffiliateMarketing.Application.Common.Interfaces;

namespace AffiliateMarketing.Infrastructure.Services;

public class DateTimeService : IDateTime
{
    // Important for Mr. Christian's central logging: 
    // Always use UtcNow to stay synced with the VM time.
    public DateTime UtcNow => DateTime.UtcNow;
}