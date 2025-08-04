"""
User feedback model for learning and improvement system.
Captures user feedback on optimizations for continuous learning.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class FeedbackType(str, Enum):
    """Type enum for different feedback categories."""
    OPTIMIZATION_QUALITY = "optimization_quality"
    USABILITY = "usability"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"


class FeedbackRating(int, Enum):
    """Rating enum for feedback scoring."""
    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class UserFeedback(Base):
    """
    Model for storing user feedback and ratings.
    
    This model captures various types of user feedback to improve
    the optimization algorithms and user experience.
    
    Attributes:
        id: Unique feedback identifier
        user_id: Reference to the user providing feedback
        optimization_id: Reference to the optimization (if applicable)
        feedback_type: Type of feedback being provided
        rating: Numeric rating (1-5 scale)
        title: Optional feedback title
        content: Detailed feedback content
        is_helpful: Whether user found the optimization helpful
        suggestions: JSON field for structured suggestions
        metadata: Additional metadata (browser, version, etc.)
        is_processed: Whether feedback has been processed by the system
        processed_at: When feedback was processed
        created_at: Feedback submission timestamp
    """
    
    __tablename__ = "user_feedback"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    optimization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prompt_optimizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Feedback classification
    feedback_type = Column(
        SQLEnum(FeedbackType),
        default=FeedbackType.GENERAL,
        nullable=False,
        index=True
    )
    
    # Rating and content
    rating = Column(Integer, nullable=True)  # 1-5 scale
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    
    # Specific optimization feedback
    is_helpful = Column(Boolean, nullable=True)  # True/False for optimization helpfulness
    
    # Structured feedback data
    suggestions = Column(JSON, nullable=True)  # Structured suggestions
    metadata = Column(JSON, nullable=True)  # Browser info, app version, etc.
    
    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    optimization = relationship("PromptOptimization")
    
    def __repr__(self) -> str:
        return f"<UserFeedback(id={self.id}, type={self.feedback_type}, user_id={self.user_id})>"
    
    def mark_processed(self) -> None:
        """Mark feedback as processed."""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
    
    @property
    def is_positive(self) -> bool:
        """Check if feedback is positive (rating >= 4 or is_helpful = True)."""
        if self.rating is not None and self.rating >= 4:
            return True
        if self.is_helpful is True:
            return True
        return False
    
    @property
    def is_negative(self) -> bool:
        """Check if feedback is negative (rating <= 2 or is_helpful = False)."""
        if self.rating is not None and self.rating <= 2:
            return True
        if self.is_helpful is False:
            return True
        return False
    
    def to_dict(self, include_user: bool = False) -> dict:
        """Convert feedback to dictionary."""
        data = {
            "id": str(self.id),
            "optimization_id": str(self.optimization_id) if self.optimization_id else None,
            "feedback_type": self.feedback_type.value if self.feedback_type else None,
            "rating": self.rating,
            "title": self.title,
            "content": self.content,
            "is_helpful": self.is_helpful,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
            "is_processed": self.is_processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_user and hasattr(self, 'user') and self.user:
            data["user"] = {
                "id": str(self.user.id),
                "username": self.user.username,
                "email": self.user.email,
            }
        
        return data