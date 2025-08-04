"""
User model for authentication and profile management.
Handles user accounts, preferences, and authentication data.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

from ..db.base import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    User model for storing user accounts and authentication data.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique)
        username: Display username (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        preferences: JSON field for user preferences
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
        login_count: Number of successful logins
    """
    
    __tablename__ = "users"
    
    # Primary key and identification
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # User preferences (JSON stored as TEXT for SQLite compatibility)
    preferences = Column(Text, nullable=True)  # JSON preferences
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Usage statistics
    login_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    prompts = relationship("Prompt", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return pwd_context.verify(password, self.hashed_password)
    
    def update_last_login(self) -> None:
        """Update last login timestamp and increment login count."""
        self.last_login = datetime.utcnow()
        self.login_count += 1
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (active account)."""
        return self.is_active
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary (exclude sensitive data by default)."""
        data = {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
        }
        
        if include_sensitive:
            data.update({
                "is_superuser": self.is_superuser,
                "preferences": self.preferences,
            })
        
        return data