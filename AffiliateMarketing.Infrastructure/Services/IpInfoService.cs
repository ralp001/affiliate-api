using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using AffiliateMarketing.Application.Common.Interfaces;

namespace AffiliateMarketing.Infrastructure.Services.Geolocation;

public class IpInfoService : IGeoLocationService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<IpInfoService> _logger;
    private readonly string _token;

    public IpInfoService(
        HttpClient httpClient,
        ILogger<IpInfoService> logger,
        IConfiguration config)
    {
        _httpClient = httpClient;
        _logger = logger;
        // Superior Quality: Token is fetched from appsettings.json
        _token = config["IpInfo:Token"] ?? throw new ArgumentNullException("IpInfo Token is missing in configuration!");
    }

    public async Task<GeoLocationData> GetLocationAsync(string ipAddress, CancellationToken ct = default)
    {
        try
        {
            // 1. Sanitize the IP (Remove port if present)
            var cleanIp = ipAddress.Split(':')[0].Trim();

            // 2. Antigravity Check: Handle local development environments
            if (IsLocal(cleanIp))
            {
                return new GeoLocationData("Localhost", "LOC", "Development", "DevRegion", "UTC");
            }

            // 3. Make the API Call
            var url = $"https://ipinfo.io/{cleanIp}?token={_token}";
            var response = await _httpClient.GetFromJsonAsync<IpInfoResponse>(url, ct);

            // 4. Return clean data
            return new GeoLocationData(
                Country: response?.Country ?? "Unknown",
                CountryCode: response?.Country ?? "XX",
                City: response?.City ?? "Unknown",
                Region: response?.Region ?? "Unknown",
                Timezone: response?.Timezone ?? "UTC"
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Antigravity Alert: Geolocation failed for IP {Ip}", ipAddress);
            return new GeoLocationData("Fallback", "XX", "Unknown", "Unknown", "UTC");
        }
    }

    private bool IsLocal(string ip) =>
        ip == "::1" || ip == "127.0.0.1" || ip.StartsWith("192.168.") || ip.StartsWith("10.");

    // Internal class to map the IpInfo JSON response
    private class IpInfoResponse
    {
        public string? Country { get; set; }
        public string? City { get; set; }
        public string? Region { get; set; }
        public string? Timezone { get; set; }
    }
}