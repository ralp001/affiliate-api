using AffiliateMarketing.Application.Identity.Commands;
using AffiliateMarketing.Domain.Entities;
using MediatR;

namespace AffiliateMarketing.Application.Identity.Handlers
{
    public sealed class RegisterUserCommandHandler
        : IRequestHandler<RegisterUserCommand>
    {
        private readonly IUserRepository _userRepository;

        public RegisterUserCommandHandler(IUserRepository userRepository)
        {
            _userRepository = userRepository;
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

            // ✅ 2. CREATE USER (HASHING STILL DONE IN INFRASTRUCTURE)
            var user = new User
            {
                Id = Guid.NewGuid(),
                Username = request.Username,
                PasswordHash = request.Password, // hashed later in Infrastructure
                Role = "Affiliate",
                CreatedAt = DateTime.UtcNow
            };

            // ✅ 3. SAVE USER
            await _userRepository.AddAsync(user, cancellationToken);
        }
    }
}
