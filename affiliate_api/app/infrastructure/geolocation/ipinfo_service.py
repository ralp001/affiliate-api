# Source: AffiliateMarketing.Infrastructure/Services/IpInfoService.cs
import httpx
from dataclasses import dataclass
from app.core.config import settings

@dataclass
class GeoLocationData:
    country: str
    country_code: str
    city: str
    region: str
    timezone: str

LOCAL_IPS = {"::1", "127.0.0.1"}

class IpInfoService:
    def __init__(self):
        self._token = settings.IPINFO_TOKEN

    def _is_local(self, ip: str) -> bool:
        return ip in LOCAL_IPS or ip.startswith("192.168.") or ip.startswith("10.")

    async def get_location(self, ip_address: str) -> GeoLocationData:
        clean_ip = ip_address.split(":")[0].strip()
        if self._is_local(clean_ip):
            return GeoLocationData("Localhost", "LOC", "Development", "DevRegion", "UTC")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"https://ipinfo.io/{clean_ip}?token={self._token}")
                resp.raise_for_status()
                data = resp.json()
                return GeoLocationData(
                    country=data.get("country", "Unknown"),
                    country_code=data.get("country", "XX"),
                    city=data.get("city", "Unknown"),
                    region=data.get("region", "Unknown"),
                    timezone=data.get("timezone", "UTC"),
                )
        except Exception:
            return GeoLocationData("Fallback", "XX", "Unknown", "Unknown", "UTC")
