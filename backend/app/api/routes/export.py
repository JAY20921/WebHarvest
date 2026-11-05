"""
Export API Routes
Endpoints for exporting extraction results
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.extraction import ExtractionJob
from app.services.export_service import export_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/export/{job_id}")
async def export_extraction_results(
    job_id: UUID,
    format: str = Query(default="json", regex="^(json|csv|xlsx)$", description="Export format"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export extraction results in specified format
    
    Formats:
    - json: JSON file
    - csv: CSV file  
    - xlsx: Excel file
    """
    try:
        # Get job
        result = await db.execute(
            select(ExtractionJob).where(ExtractionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed (status: {job.status})"
            )
        
        if not job.result_data:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Export data
        data, content_type, filename = await export_service.export_data(
            records=job.result_data,
            format=format,
        )
        
        logger.info(f"Exporting job {job_id} as {format}")
        
        # Return as downloadable file
        return Response(
            content=data if isinstance(data, bytes) else data.encode('utf-8'),
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )
