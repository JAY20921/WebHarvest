"""
Extraction Job Database Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.database import Base


class ExtractionJob(Base):
    """
    Database model for extraction jobs
    
    Stores all information about a web scraping extraction request,
    including user input, generated schema, results, and status.
    """
    __tablename__ = "extraction_jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User input
    url = Column(Text, nullable=False, comment="Source website URL")
    prompt = Column(Text, nullable=False, comment="User's extraction instruction")
    output_format = Column(
        String(10), 
        nullable=False, 
        default="json",
        comment="Desired output format: json, csv, xlsx"
    )
    
    # Job status
    status = Column(
        String(20), 
        nullable=False, 
        default="pending",
        index=True,
        comment="Job status: pending, processing, completed, failed"
    )
    
    # LLM-generated extraction schema
    extraction_schema = Column(
        JSON,
        nullable=True,
        comment="LLM-generated extraction schema as JSON"
    )
    
    # Results
    result_data = Column(
        JSON,
        nullable=True,
        comment="Extracted data as JSON (even for CSV/Excel, stored as JSON first)"
    )
    
    # Metadata
    records_count = Column(
        Integer,
        nullable=True,
        default=0,
        comment="Number of records extracted"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if job failed"
    )
    
    # Provider tracking
    llm_provider_used = Column(
        String(50),
        nullable=True,
        comment="Which LLM provider was used (groq, gemini)"
    )
    
    # Timestamps
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When job was created"
    )
    
    started_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="When job processing started"
    )
    
    completed_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="When job completed (success or failure)"
    )
    
    def __repr__(self):
        return f"<ExtractionJob(id={self.id}, url={self.url[:50]}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "job_id": str(self.id),
            "url": self.url,
            "prompt": self.prompt,
            "output_format": self.output_format,
            "status": self.status,
            "extraction_schema": self.extraction_schema,
            "result_data": self.result_data,
            "records_count": self.records_count,
            "error_message": self.error_message,
            "llm_provider_used": self.llm_provider_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
