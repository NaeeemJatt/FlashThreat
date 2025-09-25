from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.providers.factory import ProviderFactory

router = APIRouter()


@router.get("/providers", summary="Get provider information")
async def get_providers() -> Dict[str, List[Dict[str, str]]]:
    """
    Get information about available providers.
    
    Returns:
        Dictionary with provider information
    """
    try:
        providers = ProviderFactory.create_all()
        
        # Get provider information
        provider_info = []
        for name, provider in providers.items():
            provider_info.append({
                "name": name,
                "supports_types": list(provider.supports_types),
                "circuit_open": getattr(provider, 'circuit_open', False),
            })
        
        return {"providers": provider_info}
    except Exception as e:
        return {"error": str(e), "providers": []}


@router.get("/health", summary="Get system health")
async def get_health(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get system health status.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with health status
    """
    from app.core.config import settings
    from app.services.cache import RedisCache
    import asyncio
    
    health_status = {
        "status": "ok",
        "timestamp": None,
        "components": {}
    }
    
    try:
        from datetime import datetime
        health_status["timestamp"] = datetime.utcnow().isoformat()
        
        # Check database connection
        try:
            await db.execute("SELECT 1")
            health_status["components"]["database"] = {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            health_status["components"]["database"] = {"status": "unhealthy", "message": f"Database error: {str(e)}"}
            health_status["status"] = "degraded"
        
        # Check Redis connection
        try:
            cache = RedisCache()
            await cache.ping()
            health_status["components"]["redis"] = {"status": "healthy", "message": "Redis connection successful"}
        except Exception as e:
            health_status["components"]["redis"] = {"status": "unhealthy", "message": f"Redis error: {str(e)}"}
            health_status["status"] = "degraded"
        
        # Check external providers (basic connectivity)
        try:
            from app.services.providers.factory import ProviderFactory
            providers = ProviderFactory.create_all()
            provider_health = {}
            
            for name, provider in providers.items():
                try:
                    # Basic check - just see if provider can be instantiated
                    provider_health[name] = {"status": "healthy", "message": "Provider available"}
                except Exception as e:
                    provider_health[name] = {"status": "unhealthy", "message": f"Provider error: {str(e)}"}
                    health_status["status"] = "degraded"
            
            health_status["components"]["providers"] = provider_health
            
        except Exception as e:
            health_status["components"]["providers"] = {"status": "unhealthy", "message": f"Provider factory error: {str(e)}"}
            health_status["status"] = "degraded"
        
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
    
    return health_status


@router.get("/metrics", summary="Get application metrics")
async def get_metrics(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get application metrics for monitoring.
    
    Args:
        hours: Number of hours to look back for metrics
        db: Database session
        
    Returns:
        Dictionary with application metrics
    """
    from app.middleware.metrics import metrics_collector
    
    try:
        metrics = await metrics_collector.get_metrics_summary(hours)
        return metrics
    except Exception as e:
        return {
            "error": "Failed to retrieve metrics",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/performance", summary="Get performance metrics")
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get detailed performance metrics and system health.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with performance metrics
    """
    from app.core.performance import performance_monitor, database_optimizer
    
    try:
        # Get system metrics
        system_metrics = await performance_monitor.get_system_metrics()
        
        # Get performance health
        performance_health = await performance_monitor.check_performance_health()
        
        # Get database connection stats
        db_stats = await database_optimizer.get_connection_stats()
        
        # Get database optimization recommendations
        db_optimization = await database_optimizer.optimize_connections()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": system_metrics,
            "performance_health": performance_health,
            "database_stats": db_stats,
            "database_optimization": db_optimization,
        }
    except Exception as e:
        return {
            "error": "Failed to retrieve performance metrics",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/performance/optimize", summary="Optimize system performance")
async def optimize_performance(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Trigger performance optimization.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with optimization results
    """
    from app.core.performance import performance_monitor
    
    try:
        # Perform memory optimization
        memory_optimization = await performance_monitor.optimize_memory()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "optimization_results": memory_optimization,
            "status": "completed"
        }
    except Exception as e:
        return {
            "error": "Failed to optimize performance",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

