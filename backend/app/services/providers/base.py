import asyncio
import json
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.ioc_utils import IOCType


class ProviderNormalized:
    """Normalized provider response."""

    def __init__(
        self,
        provider: str,
        status: str = "ok",
        latency_ms: int = 0,
        link: str = "",
        flags: Dict[str, Any] = None,
        reputation: Optional[int] = None,
        malicious_count: Optional[int] = None,
        suspicious_count: Optional[int] = None,
        harmless_count: Optional[int] = None,
        confidence: Optional[int] = None,
        evidence: List[Dict[str, Any]] = None,
        raw: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ):
        self.provider = provider
        self.status = status
        self.latency_ms = latency_ms
        self.link = link
        self.flags = flags or {}
        self.reputation = reputation
        self.malicious_count = malicious_count
        self.suspicious_count = suspicious_count
        self.harmless_count = harmless_count
        self.confidence = confidence
        self.evidence = evidence or []
        self.raw = raw
        self.error = error

    def to_dict(self, include_raw: bool = False) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "provider": self.provider,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "link": self.link,
            "flags": self.flags,
            "reputation": self.reputation,
            "malicious_count": self.malicious_count,
            "suspicious_count": self.suspicious_count,
            "harmless_count": self.harmless_count,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }
        
        # Include error if present
        if self.error:
            result["error"] = self.error
            
        # Include raw data if requested
        if include_raw and self.raw:
            result["raw"] = self.raw
        else:
            result["raw"] = None
            
        return result


class ProviderAdapter(ABC):
    """Base class for provider adapters."""

    def __init__(self):
        self.name: str = ""
        self.supports_types: Set[IOCType] = set()
        self.failure_count = 0
        self.circuit_open = False
        self.circuit_open_until = 0

    async def fetch(
        self, ioc: str, ioc_type: IOCType, session: httpx.AsyncClient
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from the provider for the given IOC.
        
        Args:
            ioc: The IOC value
            ioc_type: The type of the IOC
            session: The HTTP session to use
            
        Returns:
            The raw provider response or None on timeout/error
        """
        # Check if circuit breaker is open
        if self.circuit_open and time.time() < self.circuit_open_until:
            return None
            
        # Check if provider supports this IOC type
        if ioc_type not in self.supports_types:
            return None
            
        try:
            response = await self._make_request(ioc, ioc_type, session)
            
            # Reset failure count on success
            self.failure_count = 0
            self.circuit_open = False
            
            return response
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            if e.response.status_code == 401:
                # Auth error
                return {"error": {"code": "auth_error", "message": "Authentication failed"}}
            elif e.response.status_code == 403:
                # Permission error (likely free tier limitation)
                return {"error": {"code": "permission_denied", "message": "API key lacks required permissions"}}
            elif e.response.status_code == 404:
                # Not found
                return {"error": {"code": "not_found", "message": "Resource not found"}}
            elif e.response.status_code == 429:
                # Rate limit
                self._increment_failure()
                return {"error": {"code": "rate_limited", "message": "Rate limit exceeded"}}
            else:
                # Other HTTP error
                self._increment_failure()
                return {"error": {"code": "http_error", "message": f"HTTP error: {e.response.status_code}"}}
        except httpx.TimeoutException:
            # Timeout
            self._increment_failure()
            return {"error": {"code": "timeout", "message": "Request timed out"}}
        except Exception as e:
            # Other error
            self._increment_failure()
            return {"error": {"code": "error", "message": str(e)}}

    @abstractmethod
    async def _make_request(
        self, ioc: str, ioc_type: IOCType, session: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """
        Make the actual request to the provider.
        
        Args:
            ioc: The IOC value
            ioc_type: The type of the IOC
            session: The HTTP session to use
            
        Returns:
            The raw provider response
        """
        pass

    @abstractmethod
    def normalize(self, raw: Dict[str, Any], ioc: str, ioc_type: IOCType) -> ProviderNormalized:
        """
        Normalize the raw provider response.
        
        Args:
            raw: The raw provider response
            ioc: The IOC value
            ioc_type: The type of the IOC
            
        Returns:
            The normalized provider response
        """
        pass

    @abstractmethod
    def link_out(self, ioc: str, ioc_type: IOCType) -> str:
        """
        Get the URL to view the IOC on the provider's site.
        
        Args:
            ioc: The IOC value
            ioc_type: The type of the IOC
            
        Returns:
            The URL to view the IOC
        """
        pass

    def _increment_failure(self) -> None:
        """Increment the failure count and check if circuit breaker should open."""
        self.failure_count += 1
        
        if self.failure_count >= settings.CIRCUIT_BREAKER_FAILS:
            self.circuit_open = True
            self.circuit_open_until = time.time() + settings.CIRCUIT_BREAKER_COOLDOWN_SEC

    async def backoff_retry(self, func, max_retries: int = 2, base_delay: float = 1.0) -> Any:
        """
        Retry a function with exponential backoff and jitter.
        
        Args:
            func: The async function to retry
            max_retries: Maximum number of retries
            base_delay: Base delay in seconds
            
        Returns:
            The function result or raises the last exception
        """
        retries = 0
        last_exception = None
        
        while retries <= max_retries:
            try:
                return await func()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    last_exception = e
                    retries += 1
                    if retries <= max_retries:
                        # Calculate delay with exponential backoff and jitter
                        delay = base_delay * (2 ** retries) * (0.5 + random.random())
                        await asyncio.sleep(delay)
                    continue
                raise  # Re-raise other HTTP errors
            except Exception as e:
                last_exception = e
                retries += 1
                if retries <= max_retries:
                    # Calculate delay with exponential backoff and jitter
                    delay = base_delay * (2 ** retries) * (0.5 + random.random())
                    await asyncio.sleep(delay)
                else:
                    break
        
        # If we've exhausted retries, raise the last exception
        if last_exception:
            raise last_exception
        
        # This should never happen
        raise Exception("Unexpected error in backoff_retry")

