"""
Pydantic Schemas for Extraction API
"""

from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class OutputFormat(str, Enum):
    """Supported output formats"""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class ExtractionStatus(str, Enum):
    """Extraction job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionRequest(BaseModel):
    """Request schema for creating extraction job"""
    url: str = Field(
        ...,
        description="Website URL to extract data from",
        example="https://example.com/products"
    )
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Natural language instruction describing what to extract",
        example="Extract all product names, prices, ratings, and review counts"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.JSON,
        description="Desired output format"
    )
    
    @validator('url')
    def validate_url(cls, v):
        """Basic URL validation"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Prompt validation"""
        if len(v.strip()) < 10:
            raise ValueError('Prompt must be at least 10 characters')
        return v.strip()


class ExtractionProgress(BaseModel):
    """Progress information for in-progress jobs"""
    step: str = Field(..., description="Current processing step")
    message: str = Field(..., description="Human-readable progress message")


class ExtractionResponse(BaseModel):
    """Response schema for extraction job status"""
    job_id: str = Field(..., description="Unique job identifier")
    url: str = Field(..., description="Source URL")
    prompt: str = Field(..., description="Extraction instruction")
    output_format: OutputFormat = Field(..., description="Output format")
    status: ExtractionStatus = Field(..., description="Current job status")
    
    # Optional fields
    records_count: Optional[int] = Field(None, description="Number of records extracted")
    data: Optional[List[dict]] = Field(None, description="Extracted data (only for completed jobs)")
    extraction_schema: Optional[dict] = Field(None, description="LLM-generated extraction schema")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    llm_provider_used: Optional[str] = Field(None, description="LLM provider used")
    
    # Progress (for processing jobs)
    progress: Optional[ExtractionProgress] = Field(None, description="Progress information")
    
    # Timestamps
    created_at: datetime = Field(..., description="When job was created")
    started_at: Optional[datetime] = Field(None, description="When processing started")
    completed_at: Optional[datetime] = Field(None, description="When job completed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "https://example.com/products",
                "prompt": "Extract product names and prices",
                "output_format": "json",
                "status": "completed",
                "records_count": 24,
                "data": [
                    {"name": "Product A", "price": 99.99},
                    {"name": "Product B", "price": 149.99}
                ],
                "created_at": "2026-11-05T10:30:00Z",
                "completed_at": "2026-11-05T10:31:00Z"
            }
        }


class ExtractionJobCreated(BaseModel):
    """Response schema for job creation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: ExtractionStatus = Field(..., description="Initial job status (always 'pending')")
    created_at: datetime = Field(..., description="When job was created")
    message: str = Field(
        default="Extraction job created successfully. Use the job_id to check status.",
        description="Success message"
    )


class HistoryListResponse(BaseModel):
    """Response schema for history list"""
    total: int = Field(..., description="Total number of jobs")
    items: List[ExtractionResponse] = Field(..., description="List of extraction jobs")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Offset for pagination")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall health status")
    services: dict = Field(..., description="Status of individual services")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "api": "ok",
                    "database": "ok",
                    "redis": "ok",
                    "llm_primary": "ok",
                    "llm_fallback": "ok"
                }
            }
        }
