from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class JobStatus(str, Enum):
    """Bulk job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BulkJob(Base):
    """Bulk job model for tracking IOC processing jobs."""
    
    __tablename__ = "bulk_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Optional user association
    status = Column(String(20), default=JobStatus.PENDING, nullable=False)
    
    # Job metadata
    total_iocs = Column(Integer, default=0, nullable=False)
    processed_iocs = Column(Integer, default=0, nullable=False)
    completed_iocs = Column(Integer, default=0, nullable=False)
    failed_iocs = Column(Integer, default=0, nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Processing details
    ioc_list = Column(JSON, nullable=False)  # List of IOCs to process
    results = Column(JSON, nullable=True)  # Processing results
    error_message = Column(Text, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Options
    force_refresh = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<BulkJob(id={self.id}, status={self.status}, total={self.total_iocs})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_iocs == 0:
            return 0.0
        return (self.processed_iocs / self.total_iocs) * 100
    
    @property
    def is_finished(self) -> bool:
        """Check if job is finished (completed, failed, or cancelled)."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "job_id": str(self.id),
            "status": self.status,
            "total_iocs": self.total_iocs,
            "processed_iocs": self.processed_iocs,
            "completed_iocs": self.completed_iocs,
            "failed_iocs": self.failed_iocs,
            "progress_percentage": round(self.progress_percentage, 2),
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "force_refresh": self.force_refresh,
            "error_message": self.error_message,
            "download_url": f"/api/bulk/{self.id}/download" if self.is_finished else None
        }
