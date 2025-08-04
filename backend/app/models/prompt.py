"""
Prompt-related models for optimization and template management.
Handles prompt storage, optimization results, and template library.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Float, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class OptimizationStatus(str, Enum):
    """Status enum for optimization tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PromptCategory(str, Enum):
    """Category enum for prompt templates."""
    GENERAL = "general"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    BUSINESS = "business"
    EDUCATIONAL = "educational"
    RESEARCH = "research"
    CUSTOM = "custom"


class Prompt(Base):
    """
    Core prompt model for storing user prompts and basic metadata.
    
    Attributes:
        id: Unique prompt identifier
        user_id: Reference to the user who created the prompt
        original_text: The original prompt text
        title: Optional title for the prompt
        description: Optional description
        category: Prompt category
        tags: JSON array of tags
        is_public: Whether the prompt can be shared publicly
        created_at: Creation timestamp
        updated_at: Last update timestamp
        usage_count: Number of times this prompt was used
    """
    
    __tablename__ = "prompts"
    
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
    
    # Prompt content
    original_text = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Classification
    category = Column(
        SQLEnum(PromptCategory),
        default=PromptCategory.GENERAL,
        nullable=False
    )
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Visibility
    is_public = Column(Boolean, default=False, nullable=False)
    
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
    
    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="prompts")
    optimizations = relationship(
        "PromptOptimization", 
        back_populates="prompt",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    def increment_usage(self) -> None:
        """Increment usage count."""
        self.usage_count += 1
    
    def to_dict(self) -> dict:
        """Convert prompt to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "original_text": self.original_text,
            "category": self.category.value if self.category else None,
            "tags": self.tags,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PromptOptimization(Base):
    """
    Model for storing optimization results and metadata.
    
    Attributes:
        id: Unique optimization identifier
        prompt_id: Reference to the original prompt
        task_id: Celery task ID for tracking background job
        status: Current optimization status
        optimized_text: The optimized prompt result
        improvement_score: Calculated improvement score (0-100)
        optimization_metadata: JSON metadata from PromptWizard
        iterations_completed: Number of optimization iterations
        processing_time: Time taken for optimization (seconds)
        error_message: Error message if optimization failed
        created_at: Optimization start timestamp
        completed_at: Optimization completion timestamp
    """
    
    __tablename__ = "prompt_optimizations"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign key to prompts
    prompt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Task tracking
    task_id = Column(String(255), unique=True, index=True, nullable=True)
    status = Column(
        SQLEnum(OptimizationStatus),
        default=OptimizationStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Optimization results
    optimized_text = Column(Text, nullable=True)
    improvement_score = Column(Float, nullable=True)  # 0-100 score
    optimization_metadata = Column(JSON, nullable=True)  # PromptWizard metadata
    
    # Processing information
    iterations_completed = Column(Integer, default=0, nullable=False)
    processing_time = Column(Float, nullable=True)  # Seconds
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    prompt = relationship("Prompt", back_populates="optimizations")
    
    def __repr__(self) -> str:
        return f"<PromptOptimization(id={self.id}, status={self.status}, prompt_id={self.prompt_id})>"
    
    def mark_completed(self, optimized_text: str, metadata: dict, score: float = None) -> None:
        """Mark optimization as completed with results."""
        self.status = OptimizationStatus.COMPLETED
        self.optimized_text = optimized_text
        self.optimization_metadata = metadata
        self.improvement_score = score
        self.completed_at = datetime.utcnow()
        
        if self.created_at:
            self.processing_time = (datetime.utcnow() - self.created_at).total_seconds()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark optimization as failed with error message."""
        self.status = OptimizationStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        
        if self.created_at:
            self.processing_time = (datetime.utcnow() - self.created_at).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert optimization to dictionary."""
        return {
            "id": str(self.id),
            "prompt_id": str(self.prompt_id),
            "task_id": self.task_id,
            "status": self.status.value if self.status else None,
            "optimized_text": self.optimized_text,
            "improvement_score": self.improvement_score,
            "optimization_metadata": self.optimization_metadata,
            "iterations_completed": self.iterations_completed,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class PromptTemplate(Base):
    """
    Model for storing reusable prompt templates.
    
    Attributes:
        id: Unique template identifier
        name: Template name
        description: Template description
        template_text: The template content with placeholders
        category: Template category
        tags: JSON array of tags
        variables: JSON array of template variables
        usage_count: Number of times template was used
        rating: Average user rating (1-5)
        rating_count: Number of ratings
        is_featured: Whether template is featured
        is_public: Whether template is publicly available
        created_by: User who created the template
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "prompt_templates"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Template information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    template_text = Column(Text, nullable=False)
    
    # Classification
    category = Column(
        SQLEnum(PromptCategory),
        default=PromptCategory.GENERAL,
        nullable=False,
        index=True
    )
    tags = Column(JSON, nullable=True)  # Array of tags
    variables = Column(JSON, nullable=True)  # Template variables schema
    
    # Usage and rating
    usage_count = Column(Integer, default=0, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)  # Average rating
    rating_count = Column(Integer, default=0, nullable=False)
    
    # Visibility and featuring
    is_featured = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Creator
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
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
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<PromptTemplate(id={self.id}, name={self.name}, category={self.category})>"
    
    def increment_usage(self) -> None:
        """Increment usage count."""
        self.usage_count += 1
    
    def add_rating(self, rating: float) -> None:
        """Add a new rating and update average."""
        total_score = self.rating * self.rating_count + rating
        self.rating_count += 1
        self.rating = total_score / self.rating_count
    
    def to_dict(self) -> dict:
        """Convert template to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "template_text": self.template_text,
            "category": self.category.value if self.category else None,
            "tags": self.tags,
            "variables": self.variables,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "is_featured": self.is_featured,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }