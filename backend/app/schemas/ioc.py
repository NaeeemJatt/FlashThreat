from typing import Literal, Optional

from pydantic import BaseModel, Field


class IOCBase(BaseModel):
    """Base schema for IOC."""
    
    value: str = Field(..., description="The IOC value")
    type: Optional[Literal["ipv4", "ipv6", "domain", "url", "hash_md5", "hash_sha1", "hash_sha256"]] = Field(
        None, description="The IOC type"
    )


class IOCCheck(BaseModel):
    """Schema for IOC check request."""
    
    ioc: str = Field(..., description="The IOC value to check")
    force_refresh: bool = Field(False, description="Whether to force refresh the cache")


class IOCResponse(BaseModel):
    """Schema for IOC response."""
    
    value: str = Field(..., description="The IOC value")
    type: str = Field(..., description="The IOC type")

