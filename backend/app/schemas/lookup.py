from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.ioc import IOCResponse
from app.schemas.provider import ProviderResult


class Summary(BaseModel):
    """Schema for lookup summary."""
    
    verdict: str = Field(..., description="Verdict (malicious, suspicious, unknown, clean)")
    score: int = Field(..., description="Score (0-100)")
    explanation: str = Field(..., description="Explanation of the verdict")
    first_seen: Optional[str] = Field(None, description="First seen timestamp")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")


class Timing(BaseModel):
    """Schema for lookup timing."""
    
    started_at: str = Field(..., description="Start timestamp")
    finished_at: str = Field(..., description="Finish timestamp")
    total_ms: int = Field(..., description="Total time in milliseconds")


class LookupResponse(BaseModel):
    """Schema for lookup response."""
    
    ioc: IOCResponse = Field(..., description="IOC information")
    summary: Summary = Field(..., description="Summary information")
    providers: List[ProviderResult] = Field(..., description="Provider results")
    timing: Timing = Field(..., description="Timing information")
    lookup_id: str = Field(..., description="Lookup ID")


class NoteCreate(BaseModel):
    """Schema for note creation."""
    
    text: str = Field(..., description="Note text")


class NoteResponse(BaseModel):
    """Schema for note response."""
    
    id: str = Field(..., description="Note ID")
    lookup_id: str = Field(..., description="Lookup ID")
    user_id: str = Field(..., description="User ID")
    text: str = Field(..., description="Note text")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True

