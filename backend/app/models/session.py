"""
User session model for tracking user activity and preferences.
Manages user sessions, preferences, and activity logging.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Boolean,
    ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class UserSession(Base):
    """
    Model for tracking user sessions and activity.
    
    Stores session information, user preferences, and activity data
    for personalization and analytics.
    
    Attributes:
        id: Unique session identifier
        user_id: Reference to the user
        session_token: JWT session token (hashed)
        ip_address: User's IP address
        user_agent: Browser/client user agent
        preferences: JSON field for session preferences
        activity_data: JSON field for activity tracking
        is_active: Whether session is currently active
        last_activity: Last activity timestamp
        created_at: Session creation timestamp
        expires_at: Session expiration timestamp
    """
    
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign key to users
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session information
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Session preferences and activity
    preferences = Column(JSON, nullable=True)  # User preferences for this session
    activity_data = Column(JSON, nullable=True)  # Activity tracking data
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_activity = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def update_activity(self, activity_type: str, data: Dict[str, Any] = None) -> None:
        """Update session activity with new activity data."""
        self.last_activity = datetime.utcnow()
        
        if self.activity_data is None:
            self.activity_data = {}
        
        # Initialize activity tracking
        if "activities" not in self.activity_data:
            self.activity_data["activities"] = []
        
        # Add new activity
        activity_entry = {
            "type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        self.activity_data["activities"].append(activity_entry)
        
        # Keep only last 100 activities to prevent unbounded growth
        if len(self.activity_data["activities"]) > 100:
            self.activity_data["activities"] = self.activity_data["activities"][-100:]
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference for this session."""
        if self.preferences is None:
            self.preferences = {}
        
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference from this session."""
        if self.preferences is None:
            return default
        
        return self.preferences.get(key, default)
    
    def deactivate(self) -> None:
        """Deactivate the session."""
        self.is_active = False
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert session to dictionary."""
        data = {
            "id": str(self.id),
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
        
        if include_sensitive:
            data.update({
                "session_token": self.session_token,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "preferences": self.preferences,
                "activity_data": self.activity_data,
            })
        
        return data