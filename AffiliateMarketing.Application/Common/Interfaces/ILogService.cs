namespace AffiliateMarketing.Application.Abstractions;

public interface ILogService
{
    Task LogAsync(Guid? userId, string action, string status, string message = "");
}