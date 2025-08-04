"""
Optimization API endpoints.
Main prompt optimization endpoints using PromptWizard framework.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.auth import (
    get_current_active_user,
    optimization_rate_limit,
    AuthenticationError
)
from ....db.session import get_db
from ....models.user import User
from ....models.prompt import Prompt
from ....services.celery_app import optimize_prompt_task, batch_optimize_task
from ....services.redis_service import redis_service
from ....services.promptwizard_service import OptimizationConfig

logger = logging.getLogger(__name__)

router = APIRouter()


class OptimizationRequest(BaseModel):
    """Request model for prompt optimization."""
    
    prompt: str = Field(..., min_length=10, max_length=5000, description="The prompt to optimize")
    task_description: Optional[str] = Field(None, max_length=1000, description="Optional task description")
    examples: Optional[List[str]] = Field(None, max_items=10, description="Optional examples")
    target_audience: Optional[str] = Field(None, max_length=500, description="Optional target audience")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional optimization configuration")
    async_processing: bool = Field(True, description="Whether to process asynchronously")
    
    @validator("examples")
    def validate_examples(cls, v):
        if v:
            for example in v:
                if len(example) > 1000:
                    raise ValueError("Each example must be less than 1000 characters")
        return v
    
    @validator("config")
    def validate_config(cls, v):
        if v:
            allowed_keys = {
                "mutate_refine_iterations", "mutation_rounds", "seen_set_size",
                "few_shot_count", "generate_reasoning", "generate_expert_identity",
                "temperature", "max_tokens"
            }
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"Invalid config key: {key}")
        return v


class BatchOptimizationRequest(BaseModel):
    """Request model for batch prompt optimization."""
    
    prompts: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50, description="List of prompts to optimize")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional batch configuration")
    
    @validator("prompts")
    def validate_prompts(cls, v):
        for i, prompt_data in enumerate(v):
            if "prompt" not in prompt_data:
                raise ValueError(f"Missing 'prompt' field in item {i}")
            if len(prompt_data["prompt"]) < 10 or len(prompt_data["prompt"]) > 5000:
                raise ValueError(f"Prompt {i} must be between 10 and 5000 characters")
        return v


class OptimizationResponse(BaseModel):
    """Response model for optimization results."""
    
    task_id: str = Field(..., description="Task ID for tracking progress")
    status: str = Field(..., description="Current status")
    message: str = Field(..., description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Optimization result if completed")
    progress: int = Field(0, description="Progress percentage (0-100)")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    
    task_id: str
    status: str
    progress: int
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    processing_time: Optional[float] = None


@router.post("/", response_model=OptimizationResponse)
async def optimize_prompt(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(optimization_rate_limit)
) -> OptimizationResponse:
    """
    Optimize a prompt using PromptWizard framework.
    
    This endpoint accepts a prompt and optimization parameters, then processes
    the optimization either synchronously or asynchronously based on the request.
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Log the optimization request
        logger.info(
            f"Optimization request received",
            extra={
                "user_id": str(current_user.id),
                "task_id": task_id,
                "prompt_length": len(request.prompt),
                "async_processing": request.async_processing
            }
        )
        
        # Store prompt in database
        prompt_record = Prompt(
            id=uuid.uuid4(),
            user_id=current_user.id,
            original_text=request.prompt,
            task_description=request.task_description,
            target_audience=request.target_audience,
            status="processing"
        )
        
        db.add(prompt_record)
        await db.commit()
        
        if request.async_processing:
            # Queue background task
            task = optimize_prompt_task.delay(
                prompt=request.prompt,
                user_id=str(current_user.id),
                task_description=request.task_description,
                examples=request.examples,
                target_audience=request.target_audience,
                config=request.config
            )
            
            # Store initial task status
            await redis_service.set_task_status(
                task_id, "pending", 0, "Optimization queued for processing"
            )
            
            return OptimizationResponse(
                task_id=task_id,
                status="pending",
                message="Optimization queued for processing",
                progress=0,
                estimated_completion=(
                    datetime.utcnow().isoformat() + "Z"
                )  # This would be calculated based on queue size
            )
        
        else:
            # Process synchronously (not recommended for production)
            return HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Synchronous processing not available. Use async_processing=true"
            )
    
    except Exception as e:
        logger.error(f"Optimization request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process optimization request: {str(e)}"
        )


@router.post("/batch", response_model=OptimizationResponse)
async def batch_optimize_prompts(
    request: BatchOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(optimization_rate_limit)
) -> OptimizationResponse:
    """
    Optimize multiple prompts in batch.
    
    This endpoint processes multiple prompts efficiently using batch optimization
    techniques. Results are returned asynchronously.
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        logger.info(
            f"Batch optimization request received",
            extra={
                "user_id": str(current_user.id),
                "task_id": task_id,
                "prompt_count": len(request.prompts)
            }
        )
        
        # Queue batch optimization task
        task = batch_optimize_task.delay(
            prompts=request.prompts,
            user_id=str(current_user.id),
            batch_config=request.config
        )
        
        # Store initial task status
        await redis_service.set_task_status(
            task_id, "pending", 0, f"Batch optimization queued for {len(request.prompts)} prompts"
        )
        
        return OptimizationResponse(
            task_id=task_id,
            status="pending",
            message=f"Batch optimization queued for {len(request.prompts)} prompts",
            progress=0
        )
    
    except Exception as e:
        logger.error(f"Batch optimization request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch optimization request: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_optimization_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
) -> TaskStatusResponse:
    """
    Get the status of an optimization task.
    
    Returns the current status, progress, and results (if completed) of an
    optimization task identified by task_id.
    """
    try:
        # Get task status from Redis
        task_status = await redis_service.get_task_status(task_id)
        
        if not task_status:
            # Try to get cached result
            cached_result = await redis_service.get_optimization_result(task_id)
            if cached_result:
                return TaskStatusResponse(
                    task_id=task_id,
                    status="completed",
                    progress=100,
                    message="Optimization completed",
                    result=cached_result["result"],
                    created_at=cached_result.get("cached_at"),
                    updated_at=cached_result.get("cached_at")
                )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Verify user has access to this task
        task_user_id = task_status.get("result", {}).get("user_id")
        if task_user_id and task_user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: task belongs to another user"
            )
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task_status["status"],
            progress=task_status["progress"],
            message=task_status.get("message"),
            result=task_status.get("result"),
            updated_at=task_status.get("updated_at")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )


@router.delete("/{task_id}")
async def cancel_optimization(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Cancel an optimization task.
    
    Attempts to cancel a running optimization task. May not be possible
    if the task has already completed or is in final stages.
    """
    try:
        # Get task status to verify ownership
        task_status = await redis_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Verify user has access to this task
        task_user_id = task_status.get("result", {}).get("user_id")
        if task_user_id and task_user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: task belongs to another user"
            )
        
        # Check if task can be cancelled
        if task_status["status"] in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task with status: {task_status['status']}"
            )
        
        # Try to revoke the Celery task
        from ....services.celery_app import celery_app
        celery_app.control.revoke(task_id, terminate=True)
        
        # Update task status
        await redis_service.set_task_status(
            task_id, "cancelled", task_status["progress"], "Task cancelled by user"
        )
        
        logger.info(f"Task {task_id} cancelled by user {current_user.id}")
        
        return {
            "message": "Task cancelled successfully",
            "task_id": task_id,
            "status": "cancelled"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


@router.get("/config/default")
async def get_default_config(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get the default optimization configuration.
    
    Returns the default PromptWizard configuration that will be used
    if no custom configuration is provided.
    """
    config = OptimizationConfig()
    
    return {
        "config": {
            "mutate_refine_iterations": config.mutate_refine_iterations,
            "mutation_rounds": config.mutation_rounds,
            "seen_set_size": config.seen_set_size,
            "few_shot_count": config.few_shot_count,
            "generate_reasoning": config.generate_reasoning,
            "generate_expert_identity": config.generate_expert_identity,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        },
        "description": "Default PromptWizard optimization configuration",
        "limits": {
            "min_prompt_length": 10,
            "max_prompt_length": 5000,
            "max_examples": 10,
            "max_batch_size": 50,
        }
    }