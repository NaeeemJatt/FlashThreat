"""
Metrics collection middleware for FlashThreat.
"""
import time
import asyncio
from typing import Dict, Any, Optional
from fastapi import Request, Response
from app.services.cache import RedisCache
from datetime import datetime, timedelta
import json


class MetricsCollector:
    """Metrics collector for application monitoring."""
    
    def __init__(self):
        self.cache = RedisCache()
        self.metrics_prefix = "flashthreat:metrics"
    
    async def record_request(self, request: Request, response: Response, duration_ms: float):
        """Record request metrics."""
        try:
            # Basic request metrics
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
            }
            
            # Store in Redis with TTL
            key = f"{self.metrics_prefix}:requests:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            await self.cache.set(key, json.dumps(metrics), ttl=86400)  # 24 hours
            
            # Update counters
            await self._update_counters(request, response)
            
        except Exception as e:
            # Don't let metrics collection break the request
            print(f"Metrics collection error: {e}")
    
    async def _update_counters(self, request: Request, response: Response):
        """Update various counters."""
        try:
            # Request count by endpoint
            endpoint_key = f"{self.metrics_prefix}:counters:endpoints:{request.url.path}"
            await self.cache.increment(endpoint_key, ttl=86400)
            
            # Request count by status code
            status_key = f"{self.metrics_prefix}:counters:status:{response.status_code}"
            await self.cache.increment(status_key, ttl=86400)
            
            # Request count by method
            method_key = f"{self.metrics_prefix}:counters:methods:{request.method}"
            await self.cache.increment(method_key, ttl=86400)
            
        except Exception as e:
            print(f"Counter update error: {e}")
    
    async def record_provider_metrics(self, provider: str, status: str, latency_ms: float, ioc_type: str):
        """Record provider-specific metrics."""
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "provider": provider,
                "status": status,
                "latency_ms": latency_ms,
                "ioc_type": ioc_type,
            }
            
            key = f"{self.metrics_prefix}:providers:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            await self.cache.set(key, json.dumps(metrics), ttl=86400)
            
            # Update provider counters
            provider_key = f"{self.metrics_prefix}:counters:providers:{provider}:{status}"
            await self.cache.increment(provider_key, ttl=86400)
            
        except Exception as e:
            print(f"Provider metrics error: {e}")
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours."""
        try:
            now = datetime.utcnow()
            summary = {
                "period_hours": hours,
                "timestamp": now.isoformat(),
                "total_requests": 0,
                "requests_by_status": {},
                "requests_by_endpoint": {},
                "requests_by_method": {},
                "provider_metrics": {},
                "average_response_time": 0,
                "error_rate": 0,
            }
            
            # Get request counts by status
            for status_code in [200, 201, 400, 401, 403, 404, 429, 500]:
                key = f"{self.metrics_prefix}:counters:status:{status_code}"
                count = await self.cache.get(key) or 0
                summary["requests_by_status"][str(status_code)] = int(count)
                summary["total_requests"] += int(count)
            
            # Get requests by endpoint
            endpoints = ["/api/check_ioc", "/api/stream_ioc", "/api/bulk", "/api/providers/health"]
            for endpoint in endpoints:
                key = f"{self.metrics_prefix}:counters:endpoints:{endpoint}"
                count = await self.cache.get(key) or 0
                summary["requests_by_endpoint"][endpoint] = int(count)
            
            # Get requests by method
            methods = ["GET", "POST", "PUT", "DELETE"]
            for method in methods:
                key = f"{self.metrics_prefix}:counters:methods:{method}"
                count = await self.cache.get(key) or 0
                summary["requests_by_method"][method] = int(count)
            
            # Calculate error rate
            error_codes = [400, 401, 403, 404, 429, 500]
            error_count = sum(summary["requests_by_status"].get(str(code), 0) for code in error_codes)
            if summary["total_requests"] > 0:
                summary["error_rate"] = (error_count / summary["total_requests"]) * 100
            
            return summary
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


# Global metrics collector
metrics_collector = MetricsCollector()


async def metrics_middleware(request: Request, call_next):
    """
    Metrics collection middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response with metrics recorded
    """
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Record metrics asynchronously (don't block response)
    asyncio.create_task(metrics_collector.record_request(request, response, duration_ms))
    
    return response
