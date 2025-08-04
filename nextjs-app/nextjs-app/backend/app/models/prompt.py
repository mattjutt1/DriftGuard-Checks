"""
Prompt model for storing original and optimized prompts.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Prompt(Base):
    """Model for storing prompt pairs (original and optimized)."""
    
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Prompt content
    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=True)
    
    # Prompt metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # creative, technical, analytical, etc.
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    
    # Optimization metadata
    optimization_type = Column(String(50), nullable=True)  # promptwizard, manual, template
    model_used = Column(String(100), nullable=True)
    temperature_used = Column(Float, nullable=True)
    
    # Quality metrics
    improvement_score = Column(Float, nullable=True)  # 0.0 to 1.0
    clarity_score = Column(Float, nullable=True)
    specificity_score = Column(Float, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    
    # Status and flags
    is_public = Column(Boolean, default=False)  # Can be shared with other users
    is_template = Column(Boolean, default=False)  # Can be used as template
    is_favorite = Column(Boolean, default=False)  # User marked as favorite
    
    # Version control
    version = Column(Integer, default=1)
    parent_prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    times_copied = Column(Integer, default=0)
    times_favorited = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="prompts")
    optimization_sessions = relationship("OptimizationSession", back_populates="prompt", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="prompt", cascade="all, delete-orphan")
    
    # Self-referential relationship for versions
    parent_prompt = relationship("Prompt", remote_side=[id], backref="child_prompts")
    
    def __repr__(self):
        return f"<Prompt(id={self.id}, title='{self.title}', user_id={self.user_id})>"