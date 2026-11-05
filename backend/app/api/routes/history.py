"""
History API Routes
Endpoints for viewing extraction history
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.api.deps import get_db
from app.models.extraction import ExtractionJob
from app.schemas.extraction import ExtractionResponse, HistoryListResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
async def get_extraction_history(
    limit: int = Query(default=20, ge=1, le=100, description="Number of jobs to return"),
    offset: int = Query(default=0, ge=0, description="Number of jobs to skip"),
    status: str = Query(default=None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> HistoryListResponse:
    """
    Get extraction job history
    
    Returns a paginated list of extraction jobs, newest first.
    """
    try:
        # Build query
        query = select(ExtractionJob).order_by(desc(ExtractionJob.created_at))
        
        # Filter by status if specified
        if status:
            query = query.where(ExtractionJob.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(ExtractionJob)
        if status:
            count_query = count_query.where(ExtractionJob.status == status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Build response items
        items = []
        for job in jobs:
            items.append(ExtractionResponse(
                job_id=str(job.id),
                url=job.url,
                prompt=job.prompt,
                output_format=job.output_format,
                status=job.status,
                records_count=job.records_count,
                error_message=job.error_message,
                llm_provider_used=job.llm_provider_used,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                # Don't include full data in history list
                data=None,
                extraction_schema=None,
            ))
        
        return HistoryListResponse(
            total=total,
            items=items,
            limit=limit,
            offset=offset,
        )
        
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )
