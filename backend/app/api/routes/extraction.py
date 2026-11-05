"""
Extraction API Routes
Endpoints for creating and managing extraction jobs
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.extraction import ExtractionJob
from app.schemas.extraction import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionJobCreated,
    ExtractionStatus,
)
from app.workers.extraction_worker import process_extraction_job
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract", response_model=ExtractionJobCreated, status_code=201)
async def create_extraction_job(
    request: ExtractionRequest,
    db: AsyncSession = Depends(get_db),
) -> ExtractionJobCreated:
    """
    Create a new extraction job
    
    The job will be processed asynchronously in the background.
    Use the returned job_id to check status with GET /api/extract/{job_id}
    """
    logger.info(f"Creating extraction job for URL: {request.url}")
    
    try:
        # Create job record
        job = ExtractionJob(
            url=request.url,
            prompt=request.prompt,
            output_format=request.output_format.value,
            status=ExtractionStatus.PENDING.value,
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Enqueue background task
        job_id_str = str(job.id)
        process_extraction_job.delay(job_id_str)
        
        logger.info(f"Extraction job created: {job_id_str}")
        
        return ExtractionJobCreated(
            job_id=job_id_str,
            status=ExtractionStatus.PENDING,
            created_at=job.created_at,
        )
        
    except Exception as e:
        logger.error(f"Failed to create extraction job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create extraction job: {str(e)}"
        )


@router.get("/extract/{job_id}", response_model=ExtractionResponse)
async def get_extraction_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ExtractionResponse:
    """
    Get extraction job status and results
    
    Returns job metadata and extracted data if completed.
    Poll this endpoint to check job progress.
    """
    try:
        # Query job
        result = await db.execute(
            select(ExtractionJob).where(ExtractionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Build response
        response = ExtractionResponse(
            job_id=str(job.id),
            url=job.url,
            prompt=job.prompt,
            output_format=job.output_format,
            status=job.status,
            records_count=job.records_count,
            data=job.result_data if job.status == 'completed' else None,
            extraction_schema=job.extraction_schema,
            error_message=job.error_message,
            llm_provider_used=job.llm_provider_used,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extraction job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve job: {str(e)}"
        )


@router.delete("/extract/{job_id}", status_code=204)
async def delete_extraction_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an extraction job and its results
    """
    try:
        result = await db.execute(
            select(ExtractionJob).where(ExtractionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        await db.delete(job)
        await db.commit()
        
        logger.info(f"Deleted extraction job: {job_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete job: {str(e)}"
        )
