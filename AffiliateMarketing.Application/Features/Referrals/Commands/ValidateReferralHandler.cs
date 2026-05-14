using MediatR;
using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Domain.Entities;
using AffiliateMarketing.Domain.Enums;
using Microsoft.EntityFrameworkCore;
using AffiliateMarketing.Application.Common.DTOs;

namespace AffiliateMarketing.Application.Features.Referrals.Commands;

public class ValidateReferralHandler : IRequestHandler<ValidateReferralCommand, ValidationResultDto>
{
    private readonly IAffiliateDbContext _context;

    public ValidateReferralHandler(IAffiliateDbContext context)
    {
        _context = context;
    }

    public async Task<ValidationResultDto> Handle(ValidateReferralCommand request, CancellationToken ct)
    {
        // 1. Fetch the Referral Link and the Owner's Profile
        var link = await _context.ReferralLinks
            .Include(l => l.AffiliateProfile)
            .FirstOrDefaultAsync(l => l.GeneratedCode == request.ReferralCode, ct);

        if (link == null || !link.IsActive)
        {
            return new ValidationResultDto(false, "Invalid or expired referral code.");
        }

        // 2. THE ANTI-FRAUD RULE: Prevent Self-Referral
        // Section 8 of Business Plan: "Security is the most important aspect"
        if (link.AffiliateProfile.UserId == request.PurchasingUserId)
        {
            // Log this attempt for the ZAP Security Report
            _context.AuditLogs.Add(new AuditLog
            {
                EntityName = "Security_Alert",
                Action = "Self_Referral_Blocked",
                NewValues = $"User: {request.PurchasingUserId} attempted to use code: {request.ReferralCode}",
                PerformedBy = request.PurchasingUserId.ToString()
            });
            await _context.SaveChangesAsync(ct);

            return new ValidationResultDto(false, "Fraud Alert: You cannot use your own referral link for discounts.");
        }

        // 3. Fetch Product to calculate the "60% of $100" logic
        var product = await _context.Products.FindAsync(request.ProductId);
        if (product == null) return new ValidationResultDto(false, "Product not found.");

        decimal calculatedCommission = 0;
        if (product.CommissionType == CommissionType.Percentage)
        {
            calculatedCommission = (product.BasePrice * product.CommissionValue) / 100;
        }
        else
        {
            calculatedCommission = product.CommissionValue;
        }

        return new ValidationResultDto(true, "Referral validated successfully.", calculatedCommission);
    }
}