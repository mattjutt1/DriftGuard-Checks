"""
History API endpoints.
User optimization history and prompt management.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from ....core.auth import get_current_active_user, standard_rate_limit
from ....db.session import get_db
from ....models.user import User
from ....models.prompt import Prompt
from ....services.redis_service import redis_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PromptHistoryResponse(BaseModel):
    """Prompt history response model."""
    
    id: str
    original_text: str
    optimized_text: Optional[str]
    task_description: Optional[str]
    target_audience: Optional[str]
    status: str
    performance_score: Optional[float]
    processing_time: Optional[float]
    improvements: Optional[List[str]]
    expert_identity: Optional[str]
    reasoning: Optional[str]
    created_at: str
    updated_at: str
    task_id: Optional[str]


class HistorySummary(BaseModel):
    """History summary model."""
    
    total_prompts: int
    successful_optimizations: int
    average_performance_score: float
    total_processing_time: float
    most_common_improvements: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    usage_stats: Dict[str, Any]


class OptimizationStats(BaseModel):
    """Optimization statistics model."""
    
    period: str
    total_optimizations: int
    success_rate: float
    average_score: float
    average_processing_time: float
    top_improvements: List[str]


@router.get("/", response_model=List[PromptHistoryResponse])
async def get_optimization_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in prompt text"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by days ago")
) -> List[PromptHistoryResponse]:
    """
    Get user's optimization history.
    
    Returns a paginated list of prompt optimizations with filtering options.
    """
    try:
        # Build base query
        query = select(Prompt).where(Prompt.user_id == current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.where(Prompt.status == status_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                Prompt.original_text.ilike(search_term) |
                Prompt.optimized_text.ilike(search_term) |
                Prompt.task_description.ilike(search_term)
            )
        
        if days:
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.where(Prompt.created_at >= since_date)
        
        # Apply ordering and pagination
        query = query.order_by(desc(Prompt.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        prompts = result.scalars().all()
        
        return [
            PromptHistoryResponse(
                id=str(prompt.id),
                original_text=prompt.original_text,
                optimized_text=prompt.optimized_text,
                task_description=prompt.task_description,
                target_audience=prompt.target_audience,
                status=prompt.status,
                performance_score=prompt.performance_score,
                processing_time=prompt.processing_time,
                improvements=prompt.improvements,
                expert_identity=prompt.expert_identity,
                reasoning=prompt.reasoning,
                created_at=prompt.created_at.isoformat(),
                updated_at=prompt.updated_at.isoformat(),
                task_id=prompt.task_id
            )
            for prompt in prompts
        ]
    
    except Exception as e:
        logger.error(f"Failed to get optimization history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve optimization history"
        )


@router.get("/{prompt_id}", response_model=PromptHistoryResponse)
async def get_prompt_detail(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PromptHistoryResponse:
    """
    Get detailed information about a specific prompt optimization.
    
    Returns complete details including optimization results and metadata.
    """
    try:
        # Get prompt by ID
        result = await db.execute(
            select(Prompt).where(
                and_(
                    Prompt.id == uuid.UUID(prompt_id),
                    Prompt.user_id == current_user.id
                )
            )
        )
        prompt = result.scalars().first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )
        
        return PromptHistoryResponse(
            id=str(prompt.id),
            original_text=prompt.original_text,
            optimized_text=prompt.optimized_text,
            task_description=prompt.task_description,
            target_audience=prompt.target_audience,
            status=prompt.status,
            performance_score=prompt.performance_score,
            processing_time=prompt.processing_time,
            improvements=prompt.improvements,
            expert_identity=prompt.expert_identity,
            reasoning=prompt.reasoning,
            created_at=prompt.created_at.isoformat(),
            updated_at=prompt.updated_at.isoformat(),
            task_id=prompt.task_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prompt details"
        )


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete a prompt from history.
    
    Permanently removes a prompt optimization record.
    """
    try:
        # Get prompt by ID
        result = await db.execute(
            select(Prompt).where(
                and_(
                    Prompt.id == uuid.UUID(prompt_id),
                    Prompt.user_id == current_user.id
                )
            )
        )
        prompt = result.scalars().first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found"
            )
        
        # Delete prompt
        await db.delete(prompt)
        await db.commit()
        
        # Clean up related cache entries
        if prompt.task_id:
            await redis_service.delete_cache(f"optimization:{prompt.task_id}")
            await redis_service.delete_cache(f"task:{prompt.task_id}")
        
        logger.info(f"Prompt deleted: {prompt_id}")
        
        return {"message": "Prompt deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prompt"
        )


@router.get("/analytics/summary", response_model=HistorySummary)
async def get_history_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Period in days for summary")
) -> HistorySummary:
    """
    Get optimization history summary and analytics.
    
    Returns aggregated statistics about user's optimization activity.
    """
    try:
        # Date range
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all prompts in period
        result = await db.execute(
            select(Prompt).where(
                and_(
                    Prompt.user_id == current_user.id,
                    Prompt.created_at >= since_date
                )
            )
        )
        prompts = result.scalars().all()
        
        if not prompts:
            return HistorySummary(
                total_prompts=0,
                successful_optimizations=0,
                average_performance_score=0.0,
                total_processing_time=0.0,
                most_common_improvements=[],
                recent_activity=[],
                usage_stats={}
            )
        
        # Calculate statistics
        total_prompts = len(prompts)
        successful_prompts = [p for p in prompts if p.status == "completed"]
        successful_optimizations = len(successful_prompts)
        
        # Average performance score
        scored_prompts = [p for p in successful_prompts if p.performance_score is not None]
        average_performance_score = (
            sum(p.performance_score for p in scored_prompts) / len(scored_prompts)
            if scored_prompts else 0.0
        )
        
        # Total processing time
        timed_prompts = [p for p in successful_prompts if p.processing_time is not None]
        total_processing_time = sum(p.processing_time for p in timed_prompts)
        
        # Most common improvements
        all_improvements = []
        for prompt in successful_prompts:
            if prompt.improvements:
                all_improvements.extend(prompt.improvements)
        
        improvement_counts = {}
        for improvement in all_improvements:
            improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1
        
        most_common_improvements = [
            {"improvement": improvement, "count": count}
            for improvement, count in sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Recent activity (last 10 prompts)
        recent_prompts = sorted(prompts, key=lambda x: x.created_at, reverse=True)[:10]
        recent_activity = [
            {
                "id": str(prompt.id),
                "status": prompt.status,
                "performance_score": prompt.performance_score,
                "created_at": prompt.created_at.isoformat(),
                "preview": prompt.original_text[:50] + "..." if len(prompt.original_text) > 50 else prompt.original_text
            }
            for prompt in recent_prompts
        ]
        
        # Usage statistics
        status_counts = {}
        for prompt in prompts:
            status_counts[prompt.status] = status_counts.get(prompt.status, 0) + 1
        
        # Daily activity (simplified)
        daily_counts = {}
        for prompt in prompts:
            day_key = prompt.created_at.date().isoformat()
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
        
        usage_stats = {
            "success_rate": round((successful_optimizations / total_prompts) * 100, 2) if total_prompts > 0 else 0,
            "status_distribution": status_counts,
            "daily_activity": dict(list(daily_counts.items())[-7:]),  # Last 7 days
            "average_processing_time": round(total_processing_time / len(timed_prompts), 2) if timed_prompts else 0
        }
        
        return HistorySummary(
            total_prompts=total_prompts,
            successful_optimizations=successful_optimizations,
            average_performance_score=round(average_performance_score, 2),
            total_processing_time=round(total_processing_time, 2),
            most_common_improvements=most_common_improvements,
            recent_activity=recent_activity,
            usage_stats=usage_stats
        )
    
    except Exception as e:
        logger.error(f"Failed to get history summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history summary"
        )


@router.get("/analytics/stats", response_model=List[OptimizationStats])
async def get_optimization_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    period: str = Query("week", regex="^(day|week|month|year)$", description="Statistics period")
) -> List[OptimizationStats]:
    """
    Get detailed optimization statistics by period.
    
    Returns time-series optimization statistics for analytics.
    """
    try:
        # Define period durations
        period_days = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365
        }
        
        days = period_days[period]
        periods_count = min(12, 365 // days)  # Max 12 periods
        
        stats_list = []
        
        for i in range(periods_count):
            end_date = datetime.utcnow() - timedelta(days=i * days)
            start_date = end_date - timedelta(days=days)
            
            # Get prompts in this period
            result = await db.execute(
                select(Prompt).where(
                    and_(
                        Prompt.user_id == current_user.id,
                        Prompt.created_at >= start_date,
                        Prompt.created_at < end_date
                    )
                )
            )
            prompts = result.scalars().all()
            
            if not prompts:
                stats_list.append(OptimizationStats(
                    period=start_date.isoformat()[:10],
                    total_optimizations=0,
                    success_rate=0.0,
                    average_score=0.0,
                    average_processing_time=0.0,
                    top_improvements=[]
                ))
                continue
            
            # Calculate statistics for this period
            total_optimizations = len(prompts)
            successful_prompts = [p for p in prompts if p.status == "completed"]
            success_rate = (len(successful_prompts) / total_optimizations) * 100 if total_optimizations > 0 else 0
            
            # Average score
            scored_prompts = [p for p in successful_prompts if p.performance_score is not None]
            average_score = (
                sum(p.performance_score for p in scored_prompts) / len(scored_prompts)
                if scored_prompts else 0.0
            )
            
            # Average processing time
            timed_prompts = [p for p in successful_prompts if p.processing_time is not None]
            average_processing_time = (
                sum(p.processing_time for p in timed_prompts) / len(timed_prompts)
                if timed_prompts else 0.0
            )
            
            # Top improvements
            all_improvements = []
            for prompt in successful_prompts:
                if prompt.improvements:
                    all_improvements.extend(prompt.improvements)
            
            improvement_counts = {}
            for improvement in all_improvements:
                improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1
            
            top_improvements = sorted(improvement_counts.keys(), key=lambda x: improvement_counts[x], reverse=True)[:3]
            
            stats_list.append(OptimizationStats(
                period=start_date.isoformat()[:10],
                total_optimizations=total_optimizations,
                success_rate=round(success_rate, 2),
                average_score=round(average_score, 2),
                average_processing_time=round(average_processing_time, 2),
                top_improvements=top_improvements
            ))
        
        # Return in chronological order
        return list(reversed(stats_list))
    
    except Exception as e:
        logger.error(f"Failed to get optimization stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve optimization statistics"
        )


@router.post("/export")
async def export_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Days to export")
) -> Dict[str, Any]:
    """
    Export optimization history.
    
    Exports user's optimization history in specified format.
    """
    try:
        # Build query
        query = select(Prompt).where(Prompt.user_id == current_user.id)
        
        if days:
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.where(Prompt.created_at >= since_date)
        
        query = query.order_by(desc(Prompt.created_at))
        
        # Execute query
        result = await db.execute(query)
        prompts = result.scalars().all()
        
        # Prepare export data
        export_data = [
            {
                "id": str(prompt.id),
                "original_text": prompt.original_text,
                "optimized_text": prompt.optimized_text,
                "task_description": prompt.task_description,
                "target_audience": prompt.target_audience,
                "status": prompt.status,
                "performance_score": prompt.performance_score,
                "processing_time": prompt.processing_time,
                "improvements": prompt.improvements,
                "expert_identity": prompt.expert_identity,
                "reasoning": prompt.reasoning,
                "created_at": prompt.created_at.isoformat(),
                "updated_at": prompt.updated_at.isoformat()
            }
            for prompt in prompts
        ]
        
        # Generate export key for download
        export_key = str(uuid.uuid4())
        
        # Cache export data temporarily
        await redis_service.set_cache(
            f"export:{export_key}",
            {
                "format": format,
                "data": export_data,
                "user_id": str(current_user.id),
                "generated_at": datetime.utcnow().isoformat()
            },
            expire=3600  # 1 hour
        )
        
        logger.info(f"History export generated for user {current_user.id}")
        
        return {
            "export_key": export_key,
            "format": format,
            "record_count": len(export_data),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "download_url": f"/api/v1/history/download/{export_key}"
        }
    
    except Exception as e:
        logger.error(f"Failed to export history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export history"
        )