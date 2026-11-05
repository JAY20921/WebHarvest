"""
Celery Worker for Extraction Jobs
Handles background processing of web scraping and data extraction
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from celery import Task
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.security import security_service
from app.services.scraping_service import scraping_service
from app.services.llm_service import llm_service
from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService
from app.services.export_service import export_service
from app.models.database import AsyncSessionLocal
from app.models.extraction import ExtractionJob
from app.core.exceptions import (
    URLValidationError,
    SSRFProtectionError,
    ScrapingError,
    LLMError,
    ExtractionError,
)
import logging

logger = logging.getLogger(__name__)


class ExtractionTask(Task):
    """Custom task class with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Task {task_id} completed successfully")
        super().on_success(retval, task_id, args, kwargs)


@celery_app.task(base=ExtractionTask, bind=True, name='extraction.process_extraction_job')
def process_extraction_job(self, job_id: str) -> Dict[str, Any]:
    """
    Process extraction job asynchronously
    
    Args:
        job_id: UUID of extraction job
        
    Returns:
        Dictionary with job results
    """
    logger.info(f"Starting extraction job: {job_id}")
    
    # Update task state
    self.update_state(
        state='PROCESSING',
        meta={'status': 'Starting extraction...'}
    )
    
    # Run async workflow
    result = asyncio.run(_process_extraction_async(job_id, self))
    
    return result


async def _process_extraction_async(job_id: str, task: Task) -> Dict[str, Any]:
    """
    Async workflow for extraction
    
    Args:
        job_id: Job ID
        task: Celery task for progress updates
        
    Returns:
        Job result dictionary
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Load job from database
            task.update_state(state='PROCESSING', meta={'status': 'Loading job...'})
            job = await _get_job(db, job_id)
            
            if not job:
                raise Exception(f"Job {job_id} not found")
            
            # Update job status
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            await db.commit()
            
            # 2. Validate URL
            task.update_state(state='PROCESSING', meta={'status': 'Validating URL...'})
            logger.info(f"Validating URL: {job.url}")
            
            try:
                await security_service.validate_extraction_url(job.url)
            except (URLValidationError, SSRFProtectionError) as e:
                raise Exception(f"URL validation failed: {str(e)}")
            
            # 3. Scrape webpage
            task.update_state(state='PROCESSING', meta={'status': 'Scraping webpage...'})
            logger.info(f"Scraping: {job.url}")
            
            try:
                scraped_data = await scraping_service.scrape_url(job.url)
                page = scraped_data['page']
                html = page.html
            except ScrapingError as e:
                raise Exception(f"Scraping failed: {str(e)}")
            
            # 4. Generate extraction schema with LLM
            task.update_state(state='PROCESSING', meta={'status': 'Analyzing with AI...'})
            logger.info("Generating extraction schema with LLM")
            
            try:
                schema, provider = await llm_service.generate_extraction_schema_from_page(
                    user_prompt=job.prompt,
                    html=html,
                )
                
                # Store schema and provider info
                job.extraction_schema = schema
                job.llm_provider_used = provider
                await db.commit()
                
            except LLMError as e:
                raise Exception(f"LLM analysis failed: {str(e)}")
            
            # 5. Extract data using schema
            task.update_state(state='PROCESSING', meta={'status': 'Extracting data...'})
            logger.info("Extracting data from page")
            
            try:
                extraction_service = ExtractionService(scraped_data['parser'])
                records = await extraction_service.extract_data(
                    schema=schema,
                    max_records=settings.MAX_RECORDS_PER_JOB,
                )
            except ExtractionError as e:
                raise Exception(f"Data extraction failed: {str(e)}")
            
            # 6. Validate extracted data
            task.update_state(state='PROCESSING', meta={'status': 'Validating results...'})
            logger.info(f"Validating {len(records)} extracted records")
            
            validation_result = ValidationService.validate_extracted_data(records, schema)
            quality_score = ValidationService.calculate_quality_score(validation_result)
            
            logger.info(
                f"Validation: {validation_result.valid_records}/{validation_result.total_records} valid, "
                f"quality score: {quality_score}"
            )
            
            # 7. Store results
            task.update_state(state='PROCESSING', meta={'status': 'Saving results...'})
            
            job.result_data = records
            job.records_count = len(records)
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Job {job_id} completed successfully: {len(records)} records extracted")
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'records_count': len(records),
                'quality_score': quality_score,
                'validation': validation_result.to_dict(),
            }
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            
            # Update job status to failed
            try:
                job = await _get_job(db, job_id)
                if job:
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.completed_at = datetime.utcnow()
                    await db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update job status: {db_error}")
            
            raise


async def _get_job(db, job_id: str):
    """Get job from database"""
    from sqlalchemy import select
    from uuid import UUID
    
    result = await db.execute(
        select(ExtractionJob).where(ExtractionJob.id == UUID(job_id))
    )
    return result.scalar_one_or_none()


@celery_app.task(name='extraction.cleanup_old_jobs')
def cleanup_old_jobs():
    """
    Periodic task to clean up old completed jobs
    """
    logger.info("Running job cleanup task")
    
    # This would be implemented to remove old jobs based on retention policy
    # For MVP, we'll keep all jobs
    
    return {'status': 'ok', 'message': 'Cleanup task completed'}
