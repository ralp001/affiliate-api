namespace AffiliateMarketing.Contracts.Identity
{
    public sealed class RegisterUserRequest
    {
        public required string Username { get; init; }
        public required string Email { get; init; }
        public required string Password { get; init; }
    }
}
