"""
User model for authentication and preferences.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User profile
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # User preferences
    preferred_language = Column(String(10), default="en")
    theme_preference = Column(String(20), default="light")  # light, dark, auto
    notification_enabled = Column(Boolean, default=True)
    
    # Advanced settings
    max_concurrent_optimizations = Column(Integer, default=3)
    default_temperature = Column(String(10), default="0.7")
    preferred_model = Column(String(100), default="qwen2.5:7b-instruct-q4_0")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Usage statistics
    total_optimizations = Column(Integer, default=0)
    successful_optimizations = Column(Integer, default=0)
    
    # Relationships
    prompts = relationship("Prompt", back_populates="user", cascade="all, delete-orphan")
    optimization_sessions = relationship("OptimizationSession", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"