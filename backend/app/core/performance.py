"""
Performance optimization utilities for FlashThreat.
"""
import asyncio
import gc
import psutil
import os
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import QueuePool
from app.core.config import settings


class PerformanceMonitor:
    """Performance monitoring and optimization utilities."""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.connection_pool_size = 20
        self.max_overflow = 30
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent / 100
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent / 100
            
            # Process-specific metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            return {
                "timestamp": asyncio.get_event_loop().time(),
                "system": {
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "used": memory.used,
                        "percent": memory.percent,
                        "threshold_exceeded": memory_percent > self.memory_threshold
                    },
                    "cpu": {
                        "percent": cpu_percent,
                        "count": psutil.cpu_count()
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": disk.percent,
                        "threshold_exceeded": disk_percent > 0.9
                    }
                },
                "process": {
                    "memory": {
                        "rss": process_memory.rss,
                        "vms": process_memory.vms
                    },
                    "cpu": process_cpu,
                    "threads": process.num_threads(),
                    "connections": len(process.connections()) if hasattr(process, 'connections') else 0
                },
                "gc": {
                    "counts": gc.get_count(),
                    "threshold": gc.get_threshold()
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def optimize_memory(self):
        """Perform memory optimization."""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Get current memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent / 100
            
            # If memory usage is high, perform aggressive cleanup
            if memory_percent > self.memory_threshold:
                # Force full garbage collection
                for generation in range(3):
                    gc.collect(generation)
                
                # Clear any cached data if possible
                # This would be application-specific
                
            return {
                "collected_objects": collected,
                "memory_percent": memory_percent,
                "optimization_performed": memory_percent > self.memory_threshold
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_performance_health(self) -> Dict[str, Any]:
        """Check overall performance health."""
        metrics = await self.get_system_metrics()
        
        if "error" in metrics:
            return {"status": "error", "message": metrics["error"]}
        
        # Check for performance issues
        issues = []
        
        # Memory issues
        if metrics["system"]["memory"]["threshold_exceeded"]:
            issues.append("High memory usage detected")
        
        # CPU issues
        if metrics["system"]["cpu"]["percent"] > 80:
            issues.append("High CPU usage detected")
        
        # Disk issues
        if metrics["system"]["disk"]["threshold_exceeded"]:
            issues.append("High disk usage detected")
        
        # Process-specific issues
        if metrics["process"]["memory"]["rss"] > 500 * 1024 * 1024:  # 500MB
            issues.append("High process memory usage")
        
        return {
            "status": "healthy" if not issues else "degraded",
            "issues": issues,
            "metrics": metrics,
            "recommendations": self._get_recommendations(metrics)
        }
    
    def _get_recommendations(self, metrics: Dict[str, Any]) -> list:
        """Get performance optimization recommendations."""
        recommendations = []
        
        # Memory recommendations
        if metrics["system"]["memory"]["percent"] > 70:
            recommendations.append("Consider increasing available memory or optimizing memory usage")
        
        # CPU recommendations
        if metrics["system"]["cpu"]["percent"] > 70:
            recommendations.append("Consider scaling horizontally or optimizing CPU-intensive operations")
        
        # Disk recommendations
        if metrics["system"]["disk"]["percent"] > 80:
            recommendations.append("Consider cleaning up disk space or increasing storage")
        
        # Process recommendations
        if metrics["process"]["memory"]["rss"] > 200 * 1024 * 1024:  # 200MB
            recommendations.append("Consider optimizing application memory usage")
        
        return recommendations


class DatabaseOptimizer:
    """Database connection and query optimization."""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.connection_pool_size = 20
        self.max_overflow = 30
        self.pool_timeout = 30
        self.pool_recycle = 3600  # 1 hour
    
    def create_optimized_engine(self) -> AsyncEngine:
        """Create an optimized database engine with connection pooling."""
        return create_async_engine(
            str(settings.POSTGRES_DSN),
            poolclass=QueuePool,
            pool_size=self.connection_pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,  # Verify connections before use
            echo=False,  # Disable SQL logging in production
        )
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection pool statistics."""
        if not self.engine:
            return {"error": "Engine not initialized"}
        
        try:
            pool = self.engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "total_connections": pool.size() + pool.overflow(),
                "available_connections": pool.checkedin(),
                "utilization_percent": (pool.checkedout() / (pool.size() + pool.overflow())) * 100 if (pool.size() + pool.overflow()) > 0 else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def optimize_connections(self):
        """Optimize database connections."""
        if not self.engine:
            return {"error": "Engine not initialized"}
        
        try:
            # Get current stats
            stats = await self.get_connection_stats()
            
            # If utilization is high, consider increasing pool size
            if stats.get("utilization_percent", 0) > 80:
                return {
                    "action": "increase_pool_size",
                    "current_utilization": stats.get("utilization_percent", 0),
                    "recommendation": "Consider increasing connection pool size"
                }
            
            return {
                "action": "no_action_needed",
                "current_utilization": stats.get("utilization_percent", 0)
            }
        except Exception as e:
            return {"error": str(e)}


# Global instances
performance_monitor = PerformanceMonitor()
database_optimizer = DatabaseOptimizer()
