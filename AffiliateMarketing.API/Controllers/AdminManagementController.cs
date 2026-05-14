using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Application.Abstractions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace AffiliateMarketing.API.Controllers;

//[Authorize(Roles = "Admin,Support")]
[ApiController]
[Route("affiliate/api/v1/admin")]
[Tags("05. System Administration")]
public class AdminManagementController : ControllerBase
{
    private readonly ILogService _logService;
    private readonly IAffiliateDbContext _context;

    public AdminManagementController(ILogService logService, IAffiliateDbContext context)
    {
        _logService = logService;
        _context = context;
    }

    /// <summary>
    /// Updates the global commission rate. 
    /// Every change is fanned out to the Unified Logs API via Kafka.
    /// </summary>
    [HttpPut("commission-rate")]
    public async Task<IActionResult> UpdateCommissionRate([FromBody] decimal newRate)
    {
        // Business Logic: Update the global setting in the DB
        // ... (Update logic here)

        // BOSS REQUIREMENT: Fan-out the change to the central audit topic
        await _logService.LogAsync(
            null,
            "Update_Global_Commission",
            "Success",
            $"Commission rate updated to {newRate}%");

        return Ok(new { Message = "Global commission rate updated successfully" });
    }

    /// <summary>
    /// Fetches audit logs for a specific entity to assist in fraud investigation.
    /// </summary>
    [HttpGet("audit-logs/{entityName}")]
    public IActionResult GetAuditLogs(string entityName)
    {
        var logs = _context.AuditLogs
            .Where(x => x.EntityName == entityName)
            .OrderByDescending(x => x.CreatedAt)
            .Take(50);

        return Ok(logs);
    }
}