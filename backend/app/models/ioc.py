import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.ioc_utils import IOCType
from app.db.base import Base


class IOCTypeEnum(str, Enum):
    """IOC types."""
    
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    DOMAIN = "domain"
    URL = "url"
    HASH_MD5 = "hash_md5"
    HASH_SHA1 = "hash_sha1"
    HASH_SHA256 = "hash_sha256"
    
    @classmethod
    def from_ioc_type(cls, ioc_type: IOCType) -> "IOCTypeEnum":
        """Convert IOCType to IOCTypeEnum."""
        return getattr(cls, ioc_type.upper())


class IOC(Base):
    """IOC model."""
    
    __tablename__ = "iocs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False)
    type = Column(SQLAEnum(IOCTypeEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<IOC {self.value} ({self.type})>"

