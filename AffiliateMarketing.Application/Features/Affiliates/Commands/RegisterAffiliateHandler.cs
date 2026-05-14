using MediatR;
using AffiliateMarketing.Application.Common.Interfaces;
using AffiliateMarketing.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace AffiliateMarketing.Application.Features.Affiliates.Commands;

public class RegisterAffiliateHandler : IRequestHandler<RegisterAffiliateCommand, Guid>
{
    private readonly IAffiliateDbContext _context;

    public RegisterAffiliateHandler(IAffiliateDbContext context)
    {
        _context = context;
    }

    public async Task<Guid> Handle(RegisterAffiliateCommand request, CancellationToken ct)
    {
        // 1. Check if the user is already an affiliate
        var existingProfile = await _context.AffiliateProfiles
            .AnyAsync(p => p.UserId == request.UserId, ct);

        if (existingProfile)
            throw new Exception("User is already registered as an affiliate.");

        // 2. Check if the TrackingId is already taken (Uniqueness check)
        var trackingIdTaken = await _context.AffiliateProfiles
            .AnyAsync(p => p.TrackingId == request.PreferredTrackingId, ct);

        if (trackingIdTaken)
            throw new Exception("This Tracking ID is already in use. Please choose another.");

        // 3. Create the profile
        var profile = new AffiliateProfile
        {
            Id = Guid.NewGuid(),
            UserId = request.UserId,
            TrackingId = request.PreferredTrackingId.ToUpper().Trim(),
            CreatedAt = DateTime.UtcNow,
            IsActive = true
        };

        _context.AffiliateProfiles.Add(profile);

        // 4. Security Audit Log
        _context.AuditLogs.Add(new AuditLog
        {
            EntityName = "AffiliateProfile",
            Action = "Register",
            NewValues = $"User: {request.UserId}, TrackingId: {profile.TrackingId}"
        });

        await _context.SaveChangesAsync(ct);
        return profile.Id;
    }
}