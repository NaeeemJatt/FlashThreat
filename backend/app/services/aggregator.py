import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import settings
from app.core.ioc_utils import IOCType, canonicalize_ioc, detect_ioc_type
from app.services.cache import RedisCache
from app.services.providers.base import ProviderNormalized
from app.services.providers.factory import ProviderFactory
from app.services.scoring import ScoringService


class FlashThreatAggregator:
    """Service for aggregating IOC data from multiple providers."""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.provider_factory = ProviderFactory
        self.scoring_service = ScoringService()
    
    async def check_ioc(
        self, ioc_value: str, force_refresh: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Check an IOC against all providers.
        
        Args:
            ioc_value: The IOC value to check
            force_refresh: Whether to force refresh the cache
            
        Returns:
            A tuple of (lookup_id, result_dict) where result_dict contains the full result
        """
        # Generate a lookup ID
        lookup_id = str(uuid.uuid4())
        
        # Detect IOC type
        ioc_type, error = detect_ioc_type(ioc_value)
        if error:
            return lookup_id, {
                "error": error,
                "ioc": {
                    "value": ioc_value,
                    "type": None
                },
                "lookup_id": lookup_id,
                "timing": {
                    "started_at": datetime.utcnow().isoformat(),
                    "finished_at": datetime.utcnow().isoformat(),
                    "total_ms": 0
                }
            }
        
        # Canonicalize the IOC
        canonical_ioc = canonicalize_ioc(ioc_value, ioc_type)
        
        # Start timing
        started_at = datetime.utcnow()
        start_time_ms = int(time.time() * 1000)
        
        # Create the result structure
        result = {
            "ioc": {
                "value": canonical_ioc,
                "type": ioc_type
            },
            "summary": {
                "verdict": "unknown",
                "score": 0,
                "explanation": "",
                "first_seen": None,
                "last_seen": None
            },
            "providers": [],
            "timing": {
                "started_at": started_at.isoformat(),
                "finished_at": None,
                "total_ms": 0
            },
            "lookup_id": lookup_id
        }
        
        # Get providers for this IOC type
        providers = self.provider_factory.create_for_ioc_type(ioc_type)
        
        # Create an HTTP client for all requests
        async with httpx.AsyncClient() as client:
            # Create tasks for each provider
            tasks = []
            for provider_name in self.provider_factory.get_provider_order():
                if provider_name in providers:
                    provider = providers[provider_name]
                    tasks.append(
                        self._check_provider(
                            provider, canonical_ioc, ioc_type, client, force_refresh
                        )
                    )
            
            # Run all tasks concurrently with individual timeouts
            provider_results = await asyncio.gather(*tasks)
            
            # Add provider results to the result
            result["providers"] = provider_results
        
        # Calculate summary
        result["summary"] = self.scoring_service.calculate_summary(provider_results)
        
        # Finish timing
        finished_at = datetime.utcnow()
        result["timing"]["finished_at"] = finished_at.isoformat()
        result["timing"]["total_ms"] = int(time.time() * 1000) - start_time_ms
        
        return lookup_id, result
    
    async def _check_provider(
        self,
        provider,
        ioc: str,
        ioc_type: IOCType,
        client: httpx.AsyncClient,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Check an IOC against a single provider.
        
        Args:
            provider: The provider adapter
            ioc: The canonicalized IOC value
            ioc_type: The IOC type
            client: The HTTP client to use
            force_refresh: Whether to force refresh the cache
            
        Returns:
            The normalized provider result
        """
        provider_name = provider.name
        
        # Check cache first if not forcing refresh
        if not force_refresh:
            cached_result = await self.cache.get_provider_result(ioc, ioc_type, provider_name)
            if cached_result:
                # Add cache age to the result
                cached_result["cached"] = True
                cached_result["cache_age_seconds"] = await self.cache.get_age_seconds(
                    ioc, ioc_type, provider_name
                )
                return cached_result
        
        # Start timing
        start_time = time.time()
        
        # Fetch from provider
        try:
            raw_result = await provider.fetch(ioc, ioc_type, client)
            
            # Normalize the result
            normalized = provider.normalize(raw_result or {}, ioc, ioc_type)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            normalized.latency_ms = latency_ms
            
            # Convert to dict
            result = normalized.to_dict(include_raw=False)
            
            # Cache the result
            await self.cache.set_provider_result(
                ioc, ioc_type, provider_name, result, raw_result
            )
            
            return result
        except Exception as e:
            # Handle any unexpected errors
            latency_ms = int((time.time() - start_time) * 1000)
            error_result = {
                "provider": provider_name,
                "status": "error",
                "latency_ms": latency_ms,
                "link": provider.link_out(ioc, ioc_type),
                "flags": {},
                "reputation": None,
                "malicious_count": None,
                "suspicious_count": None,
                "harmless_count": None,
                "confidence": None,
                "evidence": [],
                "raw": None,
                "error": {
                    "code": "error",
                    "message": str(e)
                }
            }
            return error_result

