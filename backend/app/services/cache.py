import json
import time
from typing import Any, Dict, Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.ioc_utils import IOCType


class RedisCache:
    """Redis cache for provider results."""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def _get_key(self, ioc: str, ioc_type: IOCType, provider: str) -> str:
        """
        Get Redis key for an IOC and provider.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
            
        Returns:
            Redis key
        """
        return f"ioc:{ioc_type}:{ioc}:{provider}"
    
    def _get_ttl(self, ioc_type: IOCType) -> int:
        """
        Get TTL for an IOC type.
        
        Args:
            ioc_type: The IOC type
            
        Returns:
            TTL in seconds
        """
        if ioc_type in ("ipv4", "ipv6"):
            return settings.CACHE_TTL_IP_SEC
        elif ioc_type == "domain":
            return settings.CACHE_TTL_DOMAIN_SEC
        elif ioc_type == "url":
            return settings.CACHE_TTL_URL_SEC
        elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
            return settings.CACHE_TTL_HASH_SEC
        else:
            return 3600  # Default 1 hour
    
    async def set_provider_result(
        self,
        ioc: str,
        ioc_type: IOCType,
        provider: str,
        normalized_result: Dict[str, Any],
        raw_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set provider result in cache.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
            normalized_result: The normalized result
            raw_result: The raw result
        """
        key = self._get_key(ioc, ioc_type, provider)
        ttl = self._get_ttl(ioc_type)
        
        # Store timestamp for age calculation
        normalized_result["cached_at"] = int(time.time())
        
        # Store normalized result
        await self.redis.set(key, json.dumps(normalized_result), ex=ttl)
        
        # Store raw result separately if provided
        if raw_result:
            raw_key = f"{key}:raw"
            await self.redis.set(raw_key, json.dumps(raw_result), ex=ttl)
    
    async def get_provider_result(
        self, ioc: str, ioc_type: IOCType, provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get provider result from cache.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
            
        Returns:
            The cached result or None if not found
        """
        key = self._get_key(ioc, ioc_type, provider)
        result = await self.redis.get(key)
        
        if result:
            return json.loads(result)
        
        return None
    
    async def get_raw_result(
        self, ioc: str, ioc_type: IOCType, provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get raw provider result from cache.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
            
        Returns:
            The cached raw result or None if not found
        """
        key = f"{self._get_key(ioc, ioc_type, provider)}:raw"
        result = await self.redis.get(key)
        
        if result:
            return json.loads(result)
        
        return None
    
    async def get_age_seconds(
        self, ioc: str, ioc_type: IOCType, provider: str
    ) -> Optional[int]:
        """
        Get age of cached result in seconds.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
            
        Returns:
            Age in seconds or None if not found
        """
        result = await self.get_provider_result(ioc, ioc_type, provider)
        
        if result and "cached_at" in result:
            return int(time.time()) - result["cached_at"]
        
        return None
    
    async def delete_provider_result(
        self, ioc: str, ioc_type: IOCType, provider: str
    ) -> None:
        """
        Delete provider result from cache.
        
        Args:
            ioc: The IOC value
            ioc_type: The IOC type
            provider: The provider name
        """
        key = self._get_key(ioc, ioc_type, provider)
        raw_key = f"{key}:raw"
        
        await self.redis.delete(key, raw_key)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            info = await self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                ) * 100
            }
        except Exception:
            return {"error": "Unable to get cache statistics"}
    
    async def clear_cache(self, pattern: str = "ioc:*") -> int:
        """
        Clear cache entries matching pattern.
        
        Args:
            pattern: Redis key pattern to match
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception:
            return 0

