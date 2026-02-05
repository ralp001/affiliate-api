namespace AffiliateMarketing.Domain.Entities
{
    public sealed class User
    {
        public Guid Id { get; set; }

        public required string Username { get; set; }

        public required string PasswordHash { get; set; }

        public required string Role { get; set; } // Support | Affiliate

        public DateTime CreatedAt { get; set; }
    }
}
