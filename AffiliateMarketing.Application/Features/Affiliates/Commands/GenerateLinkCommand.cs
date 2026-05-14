using MediatR;

public record GenerateLinkCommand(
    Guid AffiliateProfileId,
    Guid ProductId,
    string? SourcePlatform // FB, IG, etc.
) : IRequest<string>;