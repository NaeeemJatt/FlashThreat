from typing import Any, Dict, Set

import httpx

from app.core.config import providers_config, settings
from app.core.ioc_utils import IOCType
from app.services.providers.base import ProviderAdapter, ProviderNormalized


class AbuseIPDBAdapter(ProviderAdapter):
    """Adapter for AbuseIPDB API."""

    def __init__(self):
        super().__init__()
        self.name = "abuseipdb"
        self.supports_types: Set[IOCType] = {"ipv4"}
        self.api_key = settings.ABUSEIPDB_API_KEY
        self.base_url = providers_config.abuseipdb.base_url
        self.paths = providers_config.abuseipdb.paths

    async def _make_request(
        self, ioc: str, ioc_type: IOCType, session: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Make request to AbuseIPDB API."""
        # Only supports IP addresses
        if ioc_type != "ipv4":
            raise ValueError(f"Unsupported IOC type for AbuseIPDB: {ioc_type}")
            
        # Get the path for this IOC type
        path = self.paths.get(ioc_type)
        if not path:
            raise ValueError(f"No path configured for IOC type: {ioc_type}")
            
        url = f"{self.base_url}{path}"
        headers = {"Key": self.api_key, "Accept": "application/json"}
        params = {"ipAddress": ioc, "maxAgeInDays": 90, "verbose": True}
        
        # Make the request with retry logic
        async def _request():
            response = await session.get(
                url,
                headers=headers,
                params=params,
                timeout=httpx.Timeout(
                    connect=settings.PROVIDER_CONNECT_TIMEOUT_SEC,
                    read=settings.PROVIDER_TIMEOUT_SEC,
                    write=settings.PROVIDER_TIMEOUT_SEC,
                    pool=settings.PROVIDER_TIMEOUT_SEC,
                ),
            )
            response.raise_for_status()
            return response.json()
            
        return await self.backoff_retry(_request)

    def normalize(self, raw: Dict[str, Any], ioc: str, ioc_type: IOCType) -> ProviderNormalized:
        """Normalize AbuseIPDB response."""
        # Initialize with default values
        normalized = ProviderNormalized(
            provider=self.name,
            link=self.link_out(ioc, ioc_type),
            raw=raw
        )
        
        # Check for errors
        if "error" in raw:
            error_code = raw["error"].get("code", "error")
            error_message = raw["error"].get("message", "Unknown error")
            
            normalized.status = {
                "auth_error": "auth_error",
                "not_found": "not_found",
                "rate_limited": "rate_limited",
                "timeout": "timeout",
            }.get(error_code, "error")
            
            normalized.error = {
                "code": error_code,
                "message": error_message
            }
            
            return normalized
            
        # Extract data from the response
        data = raw.get("data", {})
        
        # Extract confidence score
        confidence_score = data.get("abuseConfidenceScore")
        if confidence_score is not None:
            normalized.confidence = confidence_score
            normalized.reputation = confidence_score  # Use confidence as reputation
        
        # Extract flags
        normalized.flags = {
            "is_public": data.get("isPublic", True),
            "is_whitelisted": data.get("isWhitelisted", False),
            "total_reports": data.get("totalReports", 0),
            "num_distinct_users": data.get("numDistinctUsers", 0),
        }
        
        # Add evidence
        normalized.evidence = []
        
        # Add geolocation evidence
        country_code = data.get("countryCode")
        country_name = data.get("countryName")
        if country_code and country_name:
            normalized.evidence.append({
                "title": "Geolocation",
                "category": "geolocation",
                "severity": "info",
                "description": f"Located in {country_name} ({country_code})",
                "attributes": {
                    "country_code": country_code,
                    "country_name": country_name
                }
            })
        
        # Add ISP evidence
        isp = data.get("isp")
        if isp:
            normalized.evidence.append({
                "title": "Network",
                "category": "network",
                "severity": "info",
                "description": f"ISP: {isp}",
                "attributes": {"isp": isp}
            })
        
        # Add usage type evidence
        usage_type = data.get("usageType")
        if usage_type:
            normalized.evidence.append({
                "title": "Usage Type",
                "category": "network",
                "severity": "info",
                "description": f"Usage: {usage_type}",
                "attributes": {"usage_type": usage_type}
            })
        
        # Add reports evidence
        total_reports = data.get("totalReports", 0)
        if total_reports > 0:
            severity = "critical" if total_reports > 100 else "high" if total_reports > 10 else "medium"
            normalized.evidence.append({
                "title": "Abuse Reports",
                "category": "reputation",
                "severity": severity,
                "description": f"Reported {total_reports} times by {data.get('numDistinctUsers', 0)} users",
                "attributes": {
                    "total_reports": total_reports,
                    "distinct_users": data.get("numDistinctUsers", 0)
                }
            })
            
            # Add recent reports if available
            reports = data.get("reports", [])
            if reports:
                categories = set()
                for report in reports[:5]:  # Take only the first 5 reports
                    categories.update(report.get("categories", []))
                
                if categories:
                    normalized.evidence.append({
                        "title": "Report Categories",
                        "category": "reputation",
                        "severity": "high",
                        "description": f"Reported for: {', '.join(str(c) for c in categories)}",
                        "attributes": {"categories": list(categories)}
                    })
        
        return normalized

    def link_out(self, ioc: str, ioc_type: IOCType) -> str:
        """Get link to AbuseIPDB UI for this IOC."""
        if ioc_type == "ipv4":
            return f"https://www.abuseipdb.com/check/{ioc}"
        else:
            return "https://www.abuseipdb.com"

