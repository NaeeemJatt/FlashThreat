from typing import Dict, List

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
) -> Dict[str, str]:
    """
    Get system health status.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with health status
    """
    # TODO: Implement proper health checks for all components
    return {"status": "ok"}

