import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.core.ioc_utils import detect_ioc_type
from app.db.base import get_db
from app.schemas.ioc import IOCCheck
from app.services.aggregator import FlashThreatAggregator
from app.services.cache import RedisCache
from app.api.routes.auth import get_current_user
from app.models.user import User

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
    from sqlalchemy import select
    from app.models.lookup import Lookup, ProviderResult, Note
    from app.models.ioc import IOC
    from app.models.user import User
    import uuid
    
    try:
        # Validate UUID format
        lookup_uuid = uuid.UUID(lookup_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lookup ID format")
    
    # Query the lookup with related data
    stmt = select(Lookup).where(Lookup.id == lookup_uuid)
    result = await db.execute(stmt)
    lookup = result.scalar_one_or_none()
    
    if not lookup:
        raise HTTPException(status_code=404, detail="Lookup not found")
    
    # Get provider results
    provider_results_stmt = select(ProviderResult).where(ProviderResult.lookup_id == lookup_uuid)
    provider_results = await db.execute(provider_results_stmt)
    provider_results_list = provider_results.scalars().all()
    
    # Get notes
    notes_stmt = select(Note).where(Note.lookup_id == lookup_uuid)
    notes = await db.execute(notes_stmt)
    notes_list = notes.scalars().all()
    
    # Get IOC details
    ioc_stmt = select(IOC).where(IOC.id == lookup.ioc_id)
    ioc_result = await db.execute(ioc_stmt)
    ioc = ioc_result.scalar_one_or_none()
    
    # Get user details
    user_stmt = select(User).where(User.id == lookup.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    return {
        "id": str(lookup.id),
        "ioc": {
            "id": str(ioc.id) if ioc else None,
            "value": ioc.value if ioc else None,
            "type": ioc.type.value if ioc else None,
        } if ioc else None,
        "user": {
            "id": str(user.id) if user else None,
            "email": user.email if user else None,
            "role": user.role.value if user else None,
        } if user else None,
        "started_at": lookup.started_at.isoformat() if lookup.started_at else None,
        "finished_at": lookup.finished_at.isoformat() if lookup.finished_at else None,
        "score": lookup.score,
        "verdict": lookup.verdict.value if lookup.verdict else None,
        "summary_json": lookup.summary_json,
        "provider_results": [
            {
                "id": str(pr.id),
                "provider": pr.provider,
                "status": pr.status,
                "latency_ms": pr.latency_ms,
                "normalized_json": pr.normalized_json,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
            }
            for pr in provider_results_list
        ],
        "notes": [
            {
                "id": str(note.id),
                "text": note.text,
                "created_at": note.created_at.isoformat() if note.created_at else None,
            }
            for note in notes_list
        ],
        "created_at": lookup.created_at.isoformat() if lookup.created_at else None,
    }


@router.get("/history", summary="Get lookup history")
async def get_lookup_history(
    limit: int = Query(50, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    user_id: Optional[str] = Query(None, description="Filter by user ID (admin only)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get lookup history with pagination.
    
    Args:
        limit: Number of records to return
        offset: Number of records to skip
        user_id: Filter by user ID (admin only)
        db: Database session
        
    Returns:
        List of lookup history records
    """
    from sqlalchemy import select, desc
    from app.models.lookup import Lookup
    from app.models.ioc import IOC
    
    # Build query
    query = select(Lookup).order_by(desc(Lookup.created_at))
    
    # Apply user filter based on role
    if current_user.role.value == "admin":
        # Admin can see all lookups or filter by specific user
        if user_id:
            query = query.where(Lookup.user_id == user_id)
    else:
        # Analyst can only see their own lookups
        query = query.where(Lookup.user_id == current_user.id)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    lookups = result.scalars().all()
    
    # Get related data for each lookup
    history_records = []
    for lookup in lookups:
        # Get IOC details
        ioc_stmt = select(IOC).where(IOC.id == lookup.ioc_id)
        ioc_result = await db.execute(ioc_stmt)
        ioc = ioc_result.scalar_one_or_none()
        
        # Get user details
        user_stmt = select(User).where(User.id == lookup.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        history_records.append({
            "id": str(lookup.id),
            "ioc": {
                "id": str(ioc.id) if ioc else None,
                "value": ioc.value if ioc else None,
                "type": ioc.type.value if ioc else None,
            } if ioc else None,
            "user": {
                "id": str(user.id) if user else None,
                "email": user.email if user else None,
                "role": user.role.value if user else None,
            } if user else None,
            "started_at": lookup.started_at.isoformat() if lookup.started_at else None,
            "finished_at": lookup.finished_at.isoformat() if lookup.finished_at else None,
            "score": lookup.score,
            "verdict": lookup.verdict.value if lookup.verdict else None,
            "summary_json": lookup.summary_json,
            "created_at": lookup.created_at.isoformat() if lookup.created_at else None,
        })
    
    # Get total count for pagination
    count_query = select(Lookup)
    if current_user.role.value == "analyst":
        count_query = count_query.where(Lookup.user_id == current_user.id)
    elif user_id:
        count_query = count_query.where(Lookup.user_id == user_id)
    
    count_result = await db.execute(count_query)
    total_count = len(count_result.scalars().all())
    
    return {
        "lookups": history_records,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
    }


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
    try:
        # Parse multipart form data
        form = await request.form()
        file = form.get("file")
        force_refresh = form.get("force_refresh", "false").lower() == "true"
        
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Create bulk processor
        from app.services.bulk_processor import BulkProcessor
        processor = BulkProcessor(db)
        
        # Create bulk job
        bulk_job = await processor.create_bulk_job(
            file_content=file_content,
            filename=file.filename,
            force_refresh=force_refresh
        )
        
        # Start background processing
        background_tasks.add_task(processor.process_bulk_job, str(bulk_job.id))
        
        return {
            "job_id": str(bulk_job.id),
            "status": bulk_job.status,
            "total_iocs": bulk_job.total_iocs,
            "message": "Bulk job submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting bulk job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
    try:
        from app.services.bulk_processor import BulkProcessor
        processor = BulkProcessor(db)
        
        progress = await processor.get_job_progress(job_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
    try:
        from app.services.bulk_processor import BulkProcessor
        processor = BulkProcessor(db)
        
        # Generate CSV content
        csv_content = await processor.generate_results_csv(job_id)
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=bulk_results_{job_id}.csv"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading job results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

