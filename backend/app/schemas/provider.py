from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Schema for evidence item."""
    
    title: str = Field(..., description="Short descriptor")
    category: str = Field(..., description="Category of evidence")
    severity: Optional[str] = Field(None, description="Severity level")
    description: str = Field(..., description="Free text description")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")


class ProviderError(BaseModel):
    """Schema for provider error."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class ProviderResult(BaseModel):
    """Schema for provider result."""
    
    provider: str = Field(..., description="Provider name")
    status: str = Field(..., description="Status of the provider result")
    latency_ms: int = Field(..., description="Latency in milliseconds")
    link: str = Field(..., description="URL to view data on provider site")
    flags: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific flags")
    reputation: Optional[int] = Field(None, description="Reputation score (0-100)")
    malicious_count: Optional[int] = Field(None, description="Count of malicious verdicts")
    suspicious_count: Optional[int] = Field(None, description="Count of suspicious verdicts")
    harmless_count: Optional[int] = Field(None, description="Count of harmless verdicts")
    confidence: Optional[int] = Field(None, description="Confidence score (0-100)")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Evidence items")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw provider response")
    error: Optional[ProviderError] = Field(None, description="Error information")
    cached: Optional[bool] = Field(None, description="Whether this result is from cache")
    cache_age_seconds: Optional[int] = Field(None, description="Age of cached result in seconds")

