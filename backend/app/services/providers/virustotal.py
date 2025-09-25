import base64
from typing import Any, Dict, Set

import httpx

from app.core.config import providers_config, settings
from app.core.ioc_utils import IOCType
from app.services.providers.base import ProviderAdapter, ProviderNormalized


class VirusTotalAdapter(ProviderAdapter):
    """Adapter for VirusTotal API."""

    def __init__(self):
        super().__init__()
        self.name = "virustotal"
        self.supports_types: Set[IOCType] = {
            "ipv4", "ipv6", "domain", "url", "hash_md5", "hash_sha1", "hash_sha256"
        }
        self.api_key = settings.VT_API_KEY
        self.base_url = providers_config.virustotal.base_url
        self.paths = providers_config.virustotal.paths

    async def _make_request(
        self, ioc: str, ioc_type: IOCType, session: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Make request to VirusTotal API."""
        # Special handling for URLs - need to encode
        if ioc_type == "url":
            ioc = base64.urlsafe_b64encode(ioc.encode()).decode().rstrip("=")
            
        # Get the path for this IOC type
        path = self.paths.get(ioc_type)
        if not path:
            raise ValueError(f"Unsupported IOC type for VirusTotal: {ioc_type}")
            
        url = f"{self.base_url}{path.format(ioc=ioc)}"
        headers = {"x-apikey": self.api_key}
        
        # Make the request with retry logic
        async def _request():
            response = await session.get(
                url,
                headers=headers,
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
        """Normalize VirusTotal response."""
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
        attributes = data.get("attributes", {})
        
        # Extract reputation data
        stats = attributes.get("last_analysis_stats", {})
        normalized.malicious_count = stats.get("malicious", 0)
        normalized.suspicious_count = stats.get("suspicious", 0)
        normalized.harmless_count = stats.get("harmless", 0)
        
        # Calculate total scans
        total_scans = sum(stats.values()) or 0
        normalized.total_scans = total_scans
        
        # Calculate detection ratio
        if total_scans > 0:
            detection_ratio = int((normalized.malicious_count / total_scans) * 100)
            normalized.detection_ratio = detection_ratio
        else:
            normalized.detection_ratio = 0
        
        # Calculate reputation score (0-100 where higher is more malicious)
        total_votes = total_scans or 1  # Avoid division by zero
        normalized.reputation = int(
            ((normalized.malicious_count * 100) + (normalized.suspicious_count * 50)) / total_votes
        )
        
        # Extract flags
        normalized.flags = {}
        
        # Add evidence based on IOC type
        normalized.evidence = []
        
        if ioc_type in ("ipv4", "ipv6"):
            # IP specific evidence
            country = attributes.get("country")
            if country:
                normalized.evidence.append({
                    "title": "Geolocation",
                    "category": "geolocation",
                    "severity": "info",
                    "description": f"Located in {country}",
                    "attributes": {"country": country}
                })
                
            asn_owner = attributes.get("as_owner")
            if asn_owner:
                normalized.evidence.append({
                    "title": "Network",
                    "category": "network",
                    "severity": "info",
                    "description": f"Owned by {asn_owner}",
                    "attributes": {"asn_owner": asn_owner}
                })
                
        elif ioc_type == "domain":
            # Domain specific evidence
            registrar = attributes.get("registrar")
            if registrar:
                normalized.evidence.append({
                    "title": "Registration",
                    "category": "whois",
                    "severity": "info",
                    "description": f"Registered through {registrar}",
                    "attributes": {"registrar": registrar}
                })
                
            creation_date = attributes.get("creation_date")
            if creation_date:
                normalized.evidence.append({
                    "title": "Domain Age",
                    "category": "whois",
                    "severity": "info",
                    "description": f"Created on {creation_date}",
                    "attributes": {"creation_date": creation_date}
                })
                
        elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
            # File hash specific evidence
            file_type = attributes.get("type_description")
            if file_type:
                normalized.evidence.append({
                    "title": "File Type",
                    "category": "file",
                    "severity": "info",
                    "description": file_type,
                    "attributes": {"file_type": file_type}
                })
                
            names = attributes.get("names", [])
            if names:
                normalized.evidence.append({
                    "title": "File Names",
                    "category": "file",
                    "severity": "info",
                    "description": f"Known as {', '.join(names[:3])}",
                    "attributes": {"names": names[:10]}
                })
        
        # Add detection evidence
        if normalized.malicious_count > 0:
            severity = "critical" if normalized.malicious_count > 10 else "high"
            normalized.evidence.append({
                "title": "Detections",
                "category": "malware",
                "severity": severity,
                "description": f"Detected as malicious by {normalized.malicious_count} engines",
                "attributes": {"detection_count": normalized.malicious_count}
            })
            
        return normalized

    def link_out(self, ioc: str, ioc_type: IOCType) -> str:
        """Get link to VirusTotal UI for this IOC."""
        base = "https://www.virustotal.com/gui"
        
        if ioc_type in ("ipv4", "ipv6"):
            return f"{base}/ip-address/{ioc}/detection"
        elif ioc_type == "domain":
            return f"{base}/domain/{ioc}/detection"
        elif ioc_type == "url":
            # URL needs to be encoded for the link
            encoded = base64.urlsafe_b64encode(ioc.encode()).decode().rstrip("=")
            return f"{base}/url/{encoded}/detection"
        elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
            return f"{base}/file/{ioc}/detection"
        else:
            return f"{base}/search/{ioc}"

