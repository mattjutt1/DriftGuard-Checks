"""
Celery application for background task processing.
Handles long-running prompt optimization jobs with progress tracking.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

from celery import Celery
from celery.signals import worker_ready, worker_shutting_down

from ..core.config import settings
from .promptwizard_service import PromptWizardService, OptimizationConfig
from .redis_service import redis_service

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "promptevolver",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.MAX_OPTIMIZATION_TIME,
    task_soft_time_limit=settings.MAX_OPTIMIZATION_TIME - 30,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    task_routes={
        "app.services.celery_tasks.optimize_prompt_task": {"queue": "optimization"},
        "app.services.celery_tasks.batch_optimize_task": {"queue": "batch"},
    },
    task_default_queue="default",
    task_create_missing_queues=True,
)


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Initialize worker when ready."""
    logger.info(f"Celery worker {sender} is ready")


@worker_shutting_down.connect
def worker_shutting_down_handler(sender=None, **kwargs):
    """Cleanup when worker shuts down."""
    logger.info(f"Celery worker {sender} is shutting down")


class AsyncTask:
    """Helper class to run async functions in Celery tasks."""
    
    @staticmethod
    def run_async(coro):
        """Run an async coroutine in the current event loop or create a new one."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="optimize_prompt_task")
def optimize_prompt_task(
    self,
    prompt: str,
    user_id: str,
    task_description: Optional[str] = None,
    examples: Optional[List[str]] = None,
    target_audience: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Background task for prompt optimization.
    
    Args:
        self: Celery task instance
        prompt: Original prompt to optimize
        user_id: User ID for tracking
        task_description: Optional task description
        examples: Optional examples
        target_audience: Optional target audience
        config: Optional optimization configuration
        
    Returns:
        Dict[str, Any]: Optimization results
    """
    task_id = self.request.id
    
    async def run_optimization():
        """Run the optimization process asynchronously."""
        try:
            # Initialize Redis service
            await redis_service.initialize()
            
            # Update task status
            await redis_service.set_task_status(
                task_id, "running", 0, "Starting optimization..."
            )
            
            # Create optimization config
            opt_config = OptimizationConfig()
            if config:
                for key, value in config.items():
                    if hasattr(opt_config, key):
                        setattr(opt_config, key, value)
            
            # Progress callback
            async def progress_callback(progress: int, message: str):
                await redis_service.set_task_status(
                    task_id, "running", progress, message
                )
                # Update Celery task state
                self.update_state(
                    state="PROGRESS",
                    meta={"current": progress, "total": 100, "message": message}
                )
            
            # Create service and run optimization
            service = PromptWizardService(opt_config)
            result = await service.optimize_prompt(
                original_prompt=prompt,
                task_description=task_description,
                examples=examples,
                target_audience=target_audience,
                progress_callback=progress_callback
            )
            
            # Prepare result data
            result_data = {
                "task_id": task_id,
                "user_id": user_id,
                "original_prompt": result.original_prompt,
                "optimized_prompt": result.optimized_prompt,
                "expert_identity": result.expert_identity,
                "reasoning": result.reasoning,
                "improvements": result.improvements,
                "performance_score": result.performance_score,
                "processing_time": result.processing_time,
                "iterations_completed": result.iterations_completed,
                "metadata": result.metadata,
                "status": "completed",
                "completed_at": result.metadata.get("timestamp"),
            }
            
            # Cache the result
            await redis_service.cache_optimization_result(task_id, result_data)
            
            # Update final task status
            await redis_service.set_task_status(
                task_id, "completed", 100, "Optimization completed successfully", result_data
            )
            
            return result_data
            
        except Exception as e:
            logger.error(f"Optimization task {task_id} failed: {e}")
            
            # Update task status with error
            error_data = {
                "task_id": task_id,
                "user_id": user_id,
                "status": "failed",
                "error": str(e),
                "failed_at": asyncio.get_event_loop().time(),
            }
            
            await redis_service.set_task_status(
                task_id, "failed", 0, f"Optimization failed: {e}", error_data
            )
            
            raise
        
        finally:
            await redis_service.close()
    
    try:
        # Run the async optimization
        return AsyncTask.run_async(run_optimization())
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "task_id": task_id}
        )
        raise


@celery_app.task(bind=True, name="batch_optimize_task")
def batch_optimize_task(
    self,
    prompts: List[Dict[str, Any]],
    user_id: str,
    batch_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Background task for batch prompt optimization.
    
    Args:
        self: Celery task instance
        prompts: List of prompts with metadata to optimize
        user_id: User ID for tracking
        batch_config: Optional batch configuration
        
    Returns:
        Dict[str, Any]: Batch optimization results
    """
    task_id = self.request.id
    
    async def run_batch_optimization():
        """Run batch optimization process asynchronously."""
        try:
            # Initialize Redis service
            await redis_service.initialize()
            
            # Update task status
            await redis_service.set_task_status(
                task_id, "running", 0, f"Starting batch optimization of {len(prompts)} prompts..."
            )
            
            results = []
            total_prompts = len(prompts)
            
            for i, prompt_data in enumerate(prompts):
                try:
                    # Progress callback for individual prompt
                    async def progress_callback(progress: int, message: str):
                        overall_progress = int((i / total_prompts + progress / (100 * total_prompts)) * 100)
                        await redis_service.set_task_status(
                            task_id, "running", overall_progress,
                            f"Processing prompt {i+1}/{total_prompts}: {message}"
                        )
                        self.update_state(
                            state="PROGRESS",
                            meta={
                                "current": overall_progress,
                                "total": 100,
                                "message": f"Processing prompt {i+1}/{total_prompts}",
                                "prompt_progress": progress
                            }
                        )
                    
                    # Create optimization config
                    opt_config = OptimizationConfig()
                    if batch_config:
                        for key, value in batch_config.items():
                            if hasattr(opt_config, key):
                                setattr(opt_config, key, value)
                    
                    # Run optimization for individual prompt
                    service = PromptWizardService(opt_config)
                    result = await service.optimize_prompt(
                        original_prompt=prompt_data["prompt"],
                        task_description=prompt_data.get("task_description"),
                        examples=prompt_data.get("examples"),
                        target_audience=prompt_data.get("target_audience"),
                        progress_callback=progress_callback
                    )
                    
                    # Add result to batch
                    result_data = {
                        "prompt_id": prompt_data.get("id", i),
                        "original_prompt": result.original_prompt,
                        "optimized_prompt": result.optimized_prompt,
                        "expert_identity": result.expert_identity,
                        "reasoning": result.reasoning,
                        "improvements": result.improvements,
                        "performance_score": result.performance_score,
                        "processing_time": result.processing_time,
                        "status": "completed",
                    }
                    
                    results.append(result_data)
                    
                    # Small delay between prompts to prevent overloading
                    await asyncio.sleep(settings.BATCH_PROCESSING_DELAY)
                    
                except Exception as e:
                    logger.error(f"Failed to optimize prompt {i+1} in batch: {e}")
                    results.append({
                        "prompt_id": prompt_data.get("id", i),
                        "original_prompt": prompt_data["prompt"],
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Prepare final batch result
            successful_count = sum(1 for r in results if r["status"] == "completed")
            failed_count = len(results) - successful_count
            
            batch_result = {
                "task_id": task_id,
                "user_id": user_id,
                "total_prompts": total_prompts,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "results": results,
                "status": "completed",
                "completed_at": asyncio.get_event_loop().time(),
            }
            
            # Cache the batch result
            await redis_service.cache_optimization_result(task_id, batch_result)
            
            # Update final task status
            await redis_service.set_task_status(
                task_id, "completed", 100,
                f"Batch optimization completed: {successful_count}/{total_prompts} successful",
                batch_result
            )
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch optimization task {task_id} failed: {e}")
            
            error_data = {
                "task_id": task_id,
                "user_id": user_id,
                "status": "failed",
                "error": str(e),
                "failed_at": asyncio.get_event_loop().time(),
            }
            
            await redis_service.set_task_status(
                task_id, "failed", 0, f"Batch optimization failed: {e}", error_data
            )
            
            raise
        
        finally:
            await redis_service.close()
    
    try:
        return AsyncTask.run_async(run_batch_optimization())
        
    except Exception as e:
        logger.error(f"Batch task execution failed: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "task_id": task_id}
        )
        raise


@celery_app.task(name="cleanup_expired_results")
def cleanup_expired_results():
    """Periodic task to clean up expired optimization results."""
    
    async def run_cleanup():
        try:
            await redis_service.initialize()
            
            # Clean up old optimization results (older than 24 hours)
            pattern = "optimization:*"
            cleaned_count = await redis_service.clear_cache_pattern(pattern)
            
            logger.info(f"Cleaned up {cleaned_count} expired optimization results")
            
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
        finally:
            await redis_service.close()
    
    AsyncTask.run_async(run_cleanup())


# Periodic task configuration
celery_app.conf.beat_schedule = {
    "cleanup-expired-results": {
        "task": "cleanup_expired_results",
        "schedule": 3600.0,  # Run every hour
    },
}


if __name__ == "__main__":
    celery_app.start()