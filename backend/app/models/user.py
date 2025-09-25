import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRole(str, Enum):
    """User roles."""
    
    ADMIN = "admin"
    ANALYST = "analyst"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.ANALYST, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User {self.email}>"

