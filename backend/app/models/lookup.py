import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class VerdictEnum(str, Enum):
    """Verdict types."""
    
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"
    CLEAN = "clean"


class Lookup(Base):
    """Lookup model."""
    
    __tablename__ = "lookups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ioc_id = Column(UUID(as_uuid=True), ForeignKey("iocs.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False)
    verdict = Column(SQLAEnum(VerdictEnum), nullable=False)
    summary_json = Column(JSON, nullable=True)
    raw_store_ref = Column(String, nullable=True)  # Reference to raw data storage
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ioc = relationship("IOC")
    user = relationship("User")
    provider_results = relationship("ProviderResult", back_populates="lookup")
    notes = relationship("Note", back_populates="lookup")
    
    def __repr__(self):
        return f"<Lookup {self.id} for IOC {self.ioc_id}>"


class ProviderResult(Base):
    """Provider result model."""
    
    __tablename__ = "provider_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lookup_id = Column(UUID(as_uuid=True), ForeignKey("lookups.id"), nullable=False)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    normalized_json = Column(JSON, nullable=False)
    raw_store_ref = Column(String, nullable=True)  # Reference to raw data storage
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    lookup = relationship("Lookup", back_populates="provider_results")
    
    def __repr__(self):
        return f"<ProviderResult {self.id} for {self.provider}>"


class Note(Base):
    """Note model."""
    
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lookup_id = Column(UUID(as_uuid=True), ForeignKey("lookups.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    lookup = relationship("Lookup", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Note {self.id} for Lookup {self.lookup_id}>"

