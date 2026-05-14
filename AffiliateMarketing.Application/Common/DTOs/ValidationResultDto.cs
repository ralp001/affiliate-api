namespace AffiliateMarketing.Application.Common.DTOs;

public record ValidationResultDto(
    bool IsValid,
    string Message,
    decimal CommissionAmount = 0
);