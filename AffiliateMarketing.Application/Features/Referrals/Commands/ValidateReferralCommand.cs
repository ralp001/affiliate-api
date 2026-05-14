using MediatR;
using AffiliateMarketing.Application.Common.DTOs;

namespace AffiliateMarketing.Application.Features.Referrals.Commands;

public record ValidateReferralCommand(
    string ReferralCode,
    Guid PurchasingUserId, // The person currently logged in and buying
    Guid ProductId
) : IRequest<ValidationResultDto>;