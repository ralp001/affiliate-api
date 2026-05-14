namespace AffiliateMarketing.Application.Common.Interfaces;

public interface IGeoLocationService
{
    Task<GeoLocationData> GetLocationAsync(string ipAddress, CancellationToken ct = default);
}

public record GeoLocationData(
    string Country,
    string CountryCode,
    string City,
    string Region,
    string Timezone);