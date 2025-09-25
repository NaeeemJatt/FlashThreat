import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ioc_utils import detect_ioc_type
from app.db.base import get_db
from app.schemas.ioc import IOCCheck
from app.services.aggregator import FlashThreatAggregator
from app.services.cache import RedisCache

router = APIRouter()


@router.post("/check_ioc", summary="Check an IOC against all providers")
async def check_ioc(
    ioc_check: IOCCheck,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Check an IOC against all providers and return the results.
    
    Args:
        ioc_check: IOC check request
        db: Database session
        
    Returns:
        Lookup response
    """
    # Initialize services
    cache = RedisCache()
    aggregator = FlashThreatAggregator(cache)
    
    # Check IOC
    lookup_id, result = await aggregator.check_ioc(
        ioc_check.ioc, force_refresh=ioc_check.force_refresh
    )
    
    # Return result
    return result


@router.get("/stream_ioc", summary="Stream IOC check results")
async def stream_ioc(
    ioc: str = Query(..., description="IOC to check"),
    force_refresh: bool = Query(False, description="Whether to force refresh the cache"),
    show_raw: bool = Query(False, description="Include raw API responses"),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Stream IOC check results as server-sent events.
    
    Args:
        ioc: IOC to check
        force_refresh: Whether to force refresh the cache
        db: Database session
        
    Returns:
        Streaming response with server-sent events
    """
    # Initialize services
    cache = RedisCache()
    aggregator = FlashThreatAggregator(cache)
    
    async def event_generator():
        # Check IOC type
        ioc_type, error = detect_ioc_type(ioc)
        if error:
            yield f"event: error\ndata: {json.dumps({'error': error})}\n\n"
            return
        
        # Start checking providers
        lookup_id, result = await aggregator.check_ioc(ioc, force_refresh=force_refresh)
        
        # Stream provider results as they arrive
        for provider_result in result["providers"]:
            # Include raw data if requested
            if show_raw and 'raw' in provider_result:
                yield f"event: provider\ndata: {json.dumps({'provider': provider_result, 'raw_data': provider_result.get('raw'), 'now_ms': result['timing']['total_ms']})}\n\n"
            else:
                yield f"event: provider\ndata: {json.dumps({'provider': provider_result, 'now_ms': result['timing']['total_ms']})}\n\n"
            # Small delay to simulate progressive loading
            await asyncio.sleep(0.1)
        
        # Stream final result
        yield f"event: done\ndata: {json.dumps(result)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/debug_ioc", summary="Get detailed IOC analysis with raw API data")
async def debug_ioc(
    ioc: str = Query(..., description="IOC to check"),
    force_refresh: bool = Query(False, description="Whether to force refresh the cache"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get detailed IOC analysis including raw API responses from all providers.
    
    Args:
        ioc: IOC to check
        force_refresh: Whether to force refresh the cache
        db: Database session
        
    Returns:
        Detailed analysis with raw API data
    """
    # Initialize services
    cache = RedisCache()
    aggregator = FlashThreatAggregator(cache)
    
    # Check IOC type
    ioc_type, error = detect_ioc_type(ioc)
    if error:
        return {"error": error}
    
    # Get detailed results with raw data
    lookup_id, result = await aggregator.check_ioc(ioc, force_refresh=force_refresh)
    
    # Enhance result with raw data from each provider
    enhanced_providers = []
    for provider_result in result["providers"]:
        enhanced_provider = provider_result.copy()
        # Include raw data if available
        if 'raw' in provider_result and provider_result['raw']:
            enhanced_provider['raw_api_response'] = provider_result['raw']
        enhanced_providers.append(enhanced_provider)
    
    result["providers"] = enhanced_providers
    result["debug_info"] = {
        "ioc": ioc,
        "ioc_type": ioc_type,
        "lookup_id": lookup_id,
        "force_refresh": force_refresh,
        "timestamp": result.get("timing", {}).get("start_time")
    }
    
    return result


@router.get("/lookup/{lookup_id}", summary="Get lookup by ID")
async def get_lookup(
    lookup_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get lookup by ID.
    
    Args:
        lookup_id: Lookup ID
        db: Database session
        
    Returns:
        Lookup response
    """
    # TODO: Implement lookup retrieval from database
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/bulk", summary="Submit bulk IOC check job")
async def submit_bulk_job(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Submit bulk IOC check job.
    
    Args:
        request: Request object
        background_tasks: Background tasks
        db: Database session
        
    Returns:
        Job ID and status
    """
    # TODO: Implement bulk job submission
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/bulk/{job_id}", summary="Get bulk job progress")
async def get_bulk_job_progress(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get bulk job progress.
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        Job progress
    """
    # TODO: Implement bulk job progress
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/bulk/{job_id}/download", summary="Download bulk job results")
async def download_bulk_job_results(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Download bulk job results.
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        CSV file with results
    """
    # TODO: Implement bulk job results download
    raise HTTPException(status_code=501, detail="Not implemented yet")

