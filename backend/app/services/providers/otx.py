from typing import Any, Dict, Set

import httpx

from app.core.config import providers_config, settings
from app.core.ioc_utils import IOCType
from app.services.providers.base import ProviderAdapter, ProviderNormalized


class OTXAdapter(ProviderAdapter):
    """Adapter for AlienVault OTX API."""

    def __init__(self):
        super().__init__()
        self.name = "otx"
        self.supports_types: Set[IOCType] = {
            "ipv4", "ipv6", "domain", "url", "hash_md5", "hash_sha1", "hash_sha256"
        }
        self.api_key = settings.OTX_API_KEY
        self.base_url = providers_config.otx.base_url
        self.paths = providers_config.otx.paths

    async def _make_request(
        self, ioc: str, ioc_type: IOCType, session: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Make request to OTX API."""
        # Get the path for this IOC type
        path = self.paths.get(ioc_type)
        if not path:
            raise ValueError(f"Unsupported IOC type for OTX: {ioc_type}")
            
        url = f"{self.base_url}{path.format(ioc=ioc)}"
        headers = {"X-OTX-API-KEY": self.api_key}
        
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
        """Normalize OTX response."""
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
        
        # Handle empty responses
        if not raw:
            normalized.status = "not_found"
            normalized.error = {
                "code": "not_found",
                "message": "No data found"
            }
            return normalized
        
        # Extract pulse count
        pulse_count = raw.get("pulse_info", {}).get("count", 0)
        
        # Extract flags
        normalized.flags = {
            "pulse_count": pulse_count,
            "validation": raw.get("validation", []),
        }
        
        # Add evidence based on IOC type
        normalized.evidence = []
        
        # Add pulse evidence
        if pulse_count > 0:
            pulses = raw.get("pulse_info", {}).get("pulses", [])
            
            # Determine severity based on pulse count
            severity = "critical" if pulse_count > 10 else "high" if pulse_count > 5 else "medium"
            
            normalized.evidence.append({
                "title": "Threat Intelligence",
                "category": "threat_intel",
                "severity": severity,
                "description": f"Found in {pulse_count} threat intelligence reports",
                "attributes": {
                    "pulse_count": pulse_count
                }
            })
            
            # Extract tags from pulses
            tags = set()
            for pulse in pulses[:10]:  # Limit to first 10 pulses
                tags.update(pulse.get("tags", []))
            
            if tags:
                normalized.evidence.append({
                    "title": "Tags",
                    "category": "classification",
                    "severity": "info",
                    "description": f"Tags: {', '.join(list(tags)[:10])}",
                    "attributes": {
                        "tags": list(tags)
                    }
                })
            
            # Extract malware families
            malware_families = set()
            for pulse in pulses:
                for tag in pulse.get("tags", []):
                    if any(prefix in tag.lower() for prefix in ["malware", "ransomware", "trojan", "backdoor"]):
                        malware_families.add(tag)
            
            if malware_families:
                normalized.evidence.append({
                    "title": "Malware Families",
                    "category": "malware",
                    "severity": "critical",
                    "description": f"Associated with malware: {', '.join(list(malware_families)[:5])}",
                    "attributes": {
                        "malware_families": list(malware_families)
                    }
                })
            
            # Extract targeted countries
            countries = set()
            for pulse in pulses:
                for tag in pulse.get("tags", []):
                    if tag.startswith("country:"):
                        countries.add(tag.split(":", 1)[1])
            
            if countries:
                normalized.evidence.append({
                    "title": "Targeted Countries",
                    "category": "targeting",
                    "severity": "medium",
                    "description": f"Targeted countries: {', '.join(list(countries))}",
                    "attributes": {
                        "countries": list(countries)
                    }
                })
            
            # Extract adversaries
            adversaries = set()
            for pulse in pulses:
                for tag in pulse.get("tags", []):
                    if any(prefix in tag.lower() for prefix in ["apt", "group", "actor", "threat-actor"]):
                        adversaries.add(tag)
            
            if adversaries:
                normalized.evidence.append({
                    "title": "Threat Actors",
                    "category": "attribution",
                    "severity": "high",
                    "description": f"Associated with threat actors: {', '.join(list(adversaries)[:5])}",
                    "attributes": {
                        "adversaries": list(adversaries)
                    }
                })
        
        # Add type-specific evidence
        if ioc_type in ("ipv4", "ipv6"):
            # IP specific evidence
            reputation = raw.get("reputation", {})
            if reputation:
                threat_score = reputation.get("threat_score")
                if threat_score is not None:
                    normalized.evidence.append({
                        "title": "Reputation",
                        "category": "reputation",
                        "severity": "high" if threat_score > 2 else "medium" if threat_score > 0 else "info",
                        "description": f"Threat score: {threat_score}",
                        "attributes": {
                            "threat_score": threat_score
                        }
                    })
            
            # Geo info
            city = raw.get("city")
            country = raw.get("country_name")
            if city or country:
                location = []
                if city:
                    location.append(city)
                if country:
                    location.append(country)
                
                normalized.evidence.append({
                    "title": "Geolocation",
                    "category": "geolocation",
                    "severity": "info",
                    "description": f"Located in {', '.join(location)}",
                    "attributes": {
                        "city": city,
                        "country": country
                    }
                })
            
            # ASN info
            asn = raw.get("asn")
            if asn:
                normalized.evidence.append({
                    "title": "Network",
                    "category": "network",
                    "severity": "info",
                    "description": f"ASN: {asn}",
                    "attributes": {
                        "asn": asn
                    }
                })
        
        elif ioc_type == "domain":
            # Domain specific evidence
            alexa_rank = raw.get("alexa")
            if alexa_rank:
                normalized.evidence.append({
                    "title": "Popularity",
                    "category": "reputation",
                    "severity": "info",
                    "description": f"Alexa rank: {alexa_rank}",
                    "attributes": {
                        "alexa_rank": alexa_rank
                    }
                })
        
        elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
            # File hash specific evidence
            analysis = raw.get("analysis", {})
            if analysis:
                plugins = analysis.get("plugins", {})
                
                # Check for file info
                file_info = plugins.get("file_info", {}).get("results", {})
                if file_info:
                    file_type = file_info.get("file_type")
                    file_size = file_info.get("file_size")
                    
                    if file_type or file_size:
                        desc_parts = []
                        if file_type:
                            desc_parts.append(f"Type: {file_type}")
                        if file_size:
                            desc_parts.append(f"Size: {file_size}")
                        
                        normalized.evidence.append({
                            "title": "File Information",
                            "category": "file",
                            "severity": "info",
                            "description": ", ".join(desc_parts),
                            "attributes": {
                                "file_type": file_type,
                                "file_size": file_size
                            }
                        })
                
                # Check for AV detections
                av_results = {}
                for plugin_name, plugin_data in plugins.items():
                    if plugin_name.startswith("av_"):
                        results = plugin_data.get("results", {})
                        detection = results.get("detection")
                        if detection:
                            av_results[plugin_name[3:]] = detection
                
                if av_results:
                    normalized.evidence.append({
                        "title": "Antivirus Detections",
                        "category": "malware",
                        "severity": "critical",
                        "description": f"Detected by {len(av_results)} antivirus engines",
                        "attributes": {
                            "av_results": av_results
                        }
                    })
        
        # Calculate reputation score based on pulse count and evidence
        reputation_score = 0
        
        # Base score from pulse count
        if pulse_count > 0:
            reputation_score += min(pulse_count * 10, 80)  # Max 80 points from pulse count
        
        # Additional points from malware evidence
        for evidence in normalized.evidence:
            if evidence["category"] == "malware" and evidence["severity"] == "critical":
                reputation_score += 20  # Add 20 points for critical malware evidence
        
        normalized.reputation = min(reputation_score, 100)  # Cap at 100
        
        # For OTX, we use pulse count as total scans and calculate detection ratio
        normalized.total_scans = pulse_count
        if pulse_count > 0:
            # Calculate detection ratio based on reputation score
            normalized.detection_ratio = min(int((reputation_score / 100) * 100), 100)
        else:
            normalized.detection_ratio = 0
        
        return normalized

    def link_out(self, ioc: str, ioc_type: IOCType) -> str:
        """Get link to OTX UI for this IOC."""
        base = "https://otx.alienvault.com/indicator"
        
        if ioc_type in ("ipv4", "ipv6"):
            return f"{base}/ip/{ioc}"
        elif ioc_type == "domain":
            return f"{base}/domain/{ioc}"
        elif ioc_type == "url":
            return f"{base}/url/{ioc}"
        elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
            return f"{base}/file/{ioc}"
        else:
            return "https://otx.alienvault.com"

