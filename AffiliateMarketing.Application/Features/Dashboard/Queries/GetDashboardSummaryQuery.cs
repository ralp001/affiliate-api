using AffiliateMarketing.Application.Features.Dashboard.Dtos;
using MediatR;

namespace AffiliateMarketing.Application.Features.Dashboard.Queries;

// The message that tells MediatR: "Go fetch the Dashboard Summary DTO"
public record GetDashboardSummaryQuery : IRequest<DashboardSummaryDto>;