from typing import List, Optional

from pydantic import BaseModel, Field


class BulkRequest(BaseModel):
    """Schema for bulk request."""
    
    iocs: List[str] = Field(..., description="List of IOCs to check")
    force_refresh: bool = Field(False, description="Whether to force refresh the cache")


class BulkProgress(BaseModel):
    """Schema for bulk progress."""
    
    job_id: str = Field(..., description="Job ID")
    total: int = Field(..., description="Total number of IOCs")
    processed: int = Field(..., description="Number of processed IOCs")
    completed: int = Field(..., description="Number of completed IOCs")
    failed: int = Field(..., description="Number of failed IOCs")
    status: str = Field(..., description="Job status")
    download_url: Optional[str] = Field(None, description="URL to download results")

