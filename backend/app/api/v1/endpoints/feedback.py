"""
Feedback API endpoints.
User feedback collection for prompt optimization improvements.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from ....core.auth import get_current_active_user, standard_rate_limit
from ....db.session import get_db
from ....models.user import User
from ....models.feedback import UserFeedback
from ....services.redis_service import redis_service

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback submission request model."""
    
    prompt_id: Optional[str] = Field(None, description="Associated prompt ID")
    task_id: Optional[str] = Field(None, description="Associated task ID")
    feedback_type: str = Field(..., description="Type of feedback")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    content: str = Field(..., min_length=10, max_length=2000, description="Feedback content")
    improvement_suggestions: Optional[List[str]] = Field(None, description="Specific improvement suggestions")
    tags: Optional[List[str]] = Field(None, max_items=10, description="Feedback tags")
    
    @validator("feedback_type")
    def validate_feedback_type(cls, v):
        allowed_types = [
            "optimization_quality",
            "speed_performance", 
            "user_experience",
            "feature_request",
            "bug_report",
            "general"
        ]
        if v not in allowed_types:
            raise ValueError(f"Invalid feedback type. Must be one of: {allowed_types}")
        return v
    
    @validator("tags")
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Each tag must be less than 50 characters")
        return v


class FeedbackResponse(BaseModel):
    """Feedback response model."""
    
    id: str
    user_id: str
    prompt_id: Optional[str]
    task_id: Optional[str]
    feedback_type: str
    rating: int
    content: str
    improvement_suggestions: Optional[List[str]]
    tags: Optional[List[str]]
    status: str
    created_at: str
    updated_at: str


class FeedbackSummary(BaseModel):
    """Feedback summary model."""
    
    total_feedback: int
    average_rating: float
    feedback_by_type: Dict[str, int]
    recent_feedback: List[FeedbackResponse]
    improvement_themes: List[Dict[str, Any]]


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(standard_rate_limit)
) -> FeedbackResponse:
    """
    Submit user feedback for prompt optimization.
    
    Collects user feedback about optimization quality, performance,
    and suggestions for improvement.
    """
    try:
        # Create feedback record
        feedback = UserFeedback(
            id=uuid.uuid4(),
            user_id=current_user.id,
            prompt_id=uuid.UUID(feedback_data.prompt_id) if feedback_data.prompt_id else None,
            task_id=feedback_data.task_id,
            feedback_type=feedback_data.feedback_type,
            rating=feedback_data.rating,
            content=feedback_data.content,
            improvement_suggestions=feedback_data.improvement_suggestions,
            tags=feedback_data.tags,
            status="submitted"
        )
        
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        
        # Cache feedback for analytics
        feedback_cache_data = {
            "user_id": str(current_user.id),
            "feedback_type": feedback_data.feedback_type,
            "rating": feedback_data.rating,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_service.set_cache(
            f"feedback_analytics:{feedback.id}",
            feedback_cache_data,
            expire=86400 * 30  # 30 days
        )
        
        logger.info(
            f"Feedback submitted",
            extra={
                "user_id": str(current_user.id),
                "feedback_id": str(feedback.id),
                "type": feedback_data.feedback_type,
                "rating": feedback_data.rating
            }
        )
        
        return FeedbackResponse(
            id=str(feedback.id),
            user_id=str(feedback.user_id),
            prompt_id=str(feedback.prompt_id) if feedback.prompt_id else None,
            task_id=feedback.task_id,
            feedback_type=feedback.feedback_type,
            rating=feedback.rating,
            content=feedback.content,
            improvement_suggestions=feedback.improvement_suggestions,
            tags=feedback.tags,
            status=feedback.status,
            created_at=feedback.created_at.isoformat(),
            updated_at=feedback.updated_at.isoformat()
        )
    
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/", response_model=List[FeedbackResponse])
async def get_user_feedback(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    feedback_type: Optional[str] = Query(None, description="Filter by feedback type")
) -> List[FeedbackResponse]:
    """
    Get user's feedback history.
    
    Returns a paginated list of feedback submitted by the current user.
    """
    try:
        # Build query
        query = select(UserFeedback).where(UserFeedback.user_id == current_user.id)
        
        if feedback_type:
            query = query.where(UserFeedback.feedback_type == feedback_type)
        
        query = query.order_by(desc(UserFeedback.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        feedback_list = result.scalars().all()
        
        return [
            FeedbackResponse(
                id=str(feedback.id),
                user_id=str(feedback.user_id),
                prompt_id=str(feedback.prompt_id) if feedback.prompt_id else None,
                task_id=feedback.task_id,
                feedback_type=feedback.feedback_type,
                rating=feedback.rating,
                content=feedback.content,
                improvement_suggestions=feedback.improvement_suggestions,
                tags=feedback.tags,
                status=feedback.status,
                created_at=feedback.created_at.isoformat(),
                updated_at=feedback.updated_at.isoformat()
            )
            for feedback in feedback_list
        ]
    
    except Exception as e:
        logger.error(f"Failed to get user feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback"
        )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_detail(
    feedback_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FeedbackResponse:
    """
    Get detailed feedback information.
    
    Returns detailed information about a specific feedback entry.
    """
    try:
        # Get feedback by ID
        result = await db.execute(
            select(UserFeedback).where(
                and_(
                    UserFeedback.id == uuid.UUID(feedback_id),
                    UserFeedback.user_id == current_user.id
                )
            )
        )
        feedback = result.scalars().first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        return FeedbackResponse(
            id=str(feedback.id),
            user_id=str(feedback.user_id),
            prompt_id=str(feedback.prompt_id) if feedback.prompt_id else None,
            task_id=feedback.task_id,
            feedback_type=feedback.feedback_type,
            rating=feedback.rating,
            content=feedback.content,
            improvement_suggestions=feedback.improvement_suggestions,
            tags=feedback.tags,
            status=feedback.status,
            created_at=feedback.created_at.isoformat(),
            updated_at=feedback.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get feedback detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback"
        )


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FeedbackResponse:
    """
    Update feedback entry.
    
    Allows users to update their feedback entries.
    """
    try:
        # Get feedback by ID
        result = await db.execute(
            select(UserFeedback).where(
                and_(
                    UserFeedback.id == uuid.UUID(feedback_id),
                    UserFeedback.user_id == current_user.id
                )
            )
        )
        feedback = result.scalars().first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Check if feedback can be updated
        if feedback.status in ["processed", "archived"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update processed or archived feedback"
            )
        
        # Update allowed fields
        allowed_fields = {
            "rating", "content", "improvement_suggestions", "tags"
        }
        
        for field, value in update_data.items():
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field}' cannot be updated"
                )
            
            if field == "rating" and not (1 <= value <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5"
                )
            
            setattr(feedback, field, value)
        
        # Update timestamp
        feedback.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(feedback)
        
        logger.info(f"Feedback updated: {feedback_id}")
        
        return FeedbackResponse(
            id=str(feedback.id),
            user_id=str(feedback.user_id),
            prompt_id=str(feedback.prompt_id) if feedback.prompt_id else None,
            task_id=feedback.task_id,
            feedback_type=feedback.feedback_type,
            rating=feedback.rating,
            content=feedback.content,
            improvement_suggestions=feedback.improvement_suggestions,
            tags=feedback.tags,
            status=feedback.status,
            created_at=feedback.created_at.isoformat(),
            updated_at=feedback.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback"
        )


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete feedback entry.
    
    Allows users to delete their feedback entries.
    """
    try:
        # Get feedback by ID
        result = await db.execute(
            select(UserFeedback).where(
                and_(
                    UserFeedback.id == uuid.UUID(feedback_id),
                    UserFeedback.user_id == current_user.id
                )
            )
        )
        feedback = result.scalars().first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Delete feedback
        await db.delete(feedback)
        await db.commit()
        
        # Remove from cache
        await redis_service.delete_cache(f"feedback_analytics:{feedback_id}")
        
        logger.info(f"Feedback deleted: {feedback_id}")
        
        return {"message": "Feedback deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feedback"
        )


@router.get("/analytics/summary", response_model=FeedbackSummary)
async def get_feedback_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FeedbackSummary:
    """
    Get feedback analytics summary for the user.
    
    Returns aggregated feedback statistics and insights.
    """
    try:
        # Get all user feedback
        result = await db.execute(
            select(UserFeedback).where(UserFeedback.user_id == current_user.id)
        )
        all_feedback = result.scalars().all()
        
        if not all_feedback:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                feedback_by_type={},
                recent_feedback=[],
                improvement_themes=[]
            )
        
        # Calculate statistics
        total_feedback = len(all_feedback)
        average_rating = sum(f.rating for f in all_feedback) / total_feedback
        
        # Feedback by type
        feedback_by_type = {}
        for feedback in all_feedback:
            feedback_by_type[feedback.feedback_type] = feedback_by_type.get(feedback.feedback_type, 0) + 1
        
        # Recent feedback (last 5)
        recent_feedback_list = sorted(all_feedback, key=lambda x: x.created_at, reverse=True)[:5]
        recent_feedback = [
            FeedbackResponse(
                id=str(feedback.id),
                user_id=str(feedback.user_id),
                prompt_id=str(feedback.prompt_id) if feedback.prompt_id else None,
                task_id=feedback.task_id,
                feedback_type=feedback.feedback_type,
                rating=feedback.rating,
                content=feedback.content[:100] + "..." if len(feedback.content) > 100 else feedback.content,
                improvement_suggestions=feedback.improvement_suggestions,
                tags=feedback.tags,
                status=feedback.status,
                created_at=feedback.created_at.isoformat(),
                updated_at=feedback.updated_at.isoformat()
            )
            for feedback in recent_feedback_list
        ]
        
        # Improvement themes (simplified analysis)
        improvement_themes = []
        if any(f.improvement_suggestions for f in all_feedback):
            improvement_themes.append({
                "theme": "Optimization Quality",
                "count": len([f for f in all_feedback if f.feedback_type == "optimization_quality"]),
                "average_rating": sum(f.rating for f in all_feedback if f.feedback_type == "optimization_quality") / 
                                max(1, len([f for f in all_feedback if f.feedback_type == "optimization_quality"]))
            })
        
        return FeedbackSummary(
            total_feedback=total_feedback,
            average_rating=round(average_rating, 2),
            feedback_by_type=feedback_by_type,
            recent_feedback=recent_feedback,
            improvement_themes=improvement_themes
        )
    
    except Exception as e:
        logger.error(f"Failed to get feedback summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback summary"
        )