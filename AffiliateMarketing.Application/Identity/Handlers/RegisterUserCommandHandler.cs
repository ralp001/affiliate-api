using Affiliate.Events;
using AffiliateMarketing.Application.Identity.Commands;
using AffiliateMarketing.Domain.Entities;
using MediatR;

namespace AffiliateMarketing.Application.Identity.Handlers;

public sealed class RegisterUserCommandHandler
    : IRequestHandler<RegisterUserCommand>
{
    private readonly IUserRepository _userRepository;
    private readonly IPublisher _publisher; // For MediatR Events

    public RegisterUserCommandHandler(IUserRepository userRepository, IPublisher publisher)
    {
        _userRepository = userRepository;
        _publisher = publisher;
    }

    public async Task Handle(
        RegisterUserCommand request,
        CancellationToken cancellationToken)
    {
        // ✅ 1. CHECK IF USERNAME ALREADY EXISTS
        var existingUser = await _userRepository
            .GetByUsernameAsync(request.Username, cancellationToken);

        if (existingUser is not null)
        {
            throw new InvalidOperationException(
                $"Username '{request.Username}' already exists.");
        }

        // ✅ 2. CREATE USER 
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = request.Username,
            PasswordHash = request.Password,
            Role = "Affiliate",
            CreatedAt = DateTime.UtcNow
        };

        // ✅ 3. SAVE USER TO DATABASE
        await _userRepository.AddAsync(user, cancellationToken);

        // ✅ 4. NOTIFY KAFKA (For the Ops Team & Logs API)
        await _publisher.Publish(new AffiliateRegisteredEvent
        {
            AffiliateId = user.Id,
            BusinessName = user.Username, // Using Username as the initial name
            Email = "pending@update.com", // Placeholder or from request
            Region = "Default",
            RegisteredAt = user.CreatedAt
        }, cancellationToken);
    }
}