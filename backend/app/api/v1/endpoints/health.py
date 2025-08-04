"""
Health check and system monitoring endpoints.
Provides comprehensive system health information and monitoring capabilities.
"""

import logging
import time
import psutil
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

try:
    import psutil
except ImportError:
    psutil = None

from ....core.auth import get_current_superuser, get_optional_user
from ....models.user import User
from ....services.ollama_client import OllamaClient
from ....services.redis_service import redis_service
from ....db.session import engine

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""
    
    status: str
    timestamp: str
    version: str
    uptime: float
    services: Dict[str, Any]
    system: Dict[str, Any] = None


class DetailedHealthStatus(BaseModel):
    """Detailed health status for admin users."""
    
    status: str
    timestamp: str
    version: str
    uptime: float
    services: Dict[str, Any]
    system: Dict[str, Any]
    performance: Dict[str, Any]
    dependencies: Dict[str, Any]


@router.get("/", response_model=HealthStatus)
async def basic_health_check(
    current_user: User = Depends(get_optional_user)
) -> HealthStatus:
    """
    Basic health check for system status.
    
    Returns essential health information available to all users.
    Provides more detail for authenticated users.
    """
    start_time = time.time()
    
    try:
        # Check core services
        services = {}
        
        # Database health
        try:
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            services["database"] = {
                "status": "healthy",
                "type": "SQLite" if "sqlite" in str(engine.url) else "PostgreSQL"
            }
        except Exception as e:
            services["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Redis health
        try:
            redis_ping = await redis_service.ping()
            services["redis"] = {
                "status": "healthy" if redis_ping else "unhealthy"
            }
        except Exception as e:
            services["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Ollama health (basic check)
        try:
            async with OllamaClient() as ollama:
                ollama_health = await ollama.health_check()
                services["ollama"] = {
                    "status": ollama_health["status"],
                    "model": ollama_health.get("model"),
                    "response_time": ollama_health.get("response_time")
                }
        except Exception as e:
            services["ollama"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Overall system status
        unhealthy_services = [name for name, service in services.items() 
                            if service["status"] != "healthy"]
        overall_status = "unhealthy" if unhealthy_services else "healthy"
        
        # System info (basic for all users)
        system_info = None
        if current_user:
            system_info = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        
        processing_time = time.time() - start_time
        
        return HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="2.0.0",
            uptime=processing_time,
            services=services,
            system=system_info
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(
            status="error",
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="2.0.0",
            uptime=time.time() - start_time,
            services={"error": str(e)},
            system=None
        )


@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check(
    current_user: User = Depends(get_current_superuser)
) -> DetailedHealthStatus:
    """
    Detailed health check for administrators.
    
    Returns comprehensive system health information including
    performance metrics, dependency status, and system resources.
    """
    start_time = time.time()
    
    try:
        # Core services (same as basic)
        services = {}
        
        # Database health with connection info
        try:
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                row = result.fetchone()
            
            services["database"] = {
                "status": "healthy",
                "type": "SQLite" if "sqlite" in str(engine.url) else "PostgreSQL",
                "url": str(engine.url).split("@")[-1] if "@" in str(engine.url) else "local",
                "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else "N/A",
                "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else "N/A"
            }
        except Exception as e:
            services["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Redis health with stats
        try:
            redis_ping = await redis_service.ping()
            if redis_ping:
                redis_stats = await redis_service.get_cache_stats()
                services["redis"] = {
                    "status": "healthy",
                    "stats": redis_stats
                }
            else:
                services["redis"] = {"status": "unhealthy"}
        except Exception as e:
            services["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Ollama health with model info
        try:
            async with OllamaClient() as ollama:
                ollama_health = await ollama.health_check()
                model_info = await ollama.get_model_info()
                services["ollama"] = {
                    "status": ollama_health["status"],
                    "model": ollama_health.get("model"),
                    "response_time": ollama_health.get("response_time"),
                    "model_info": {
                        "size": model_info.get("details", {}).get("parameter_size"),
                        "format": model_info.get("details", {}).get("format"),
                        "family": model_info.get("details", {}).get("family")
                    }
                }
        except Exception as e:
            services["ollama"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # System information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        system_info = {
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True)
            },
            "memory": {
                "usage_percent": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2)
            },
            "disk": {
                "usage_percent": disk.percent,
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2)
            },
            "system": {
                "platform": psutil.LINUX,
                "boot_time": boot_time.isoformat(),
                "uptime_hours": round((datetime.now() - boot_time).total_seconds() / 3600, 2)
            }
        }
        
        # Performance metrics
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        performance = {
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            },
            "processes": {
                "total": len(psutil.pids()),
                "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running'])
            }
        }
        
        # Dependencies status
        dependencies = {
            "python_version": f"{psutil.version_info.major}.{psutil.version_info.minor}.{psutil.version_info.micro}",
            "fastapi": "0.104.1",  # From requirements.txt
            "sqlalchemy": "2.0.23",
            "redis": "5.0.1",
            "celery": "5.3.4"
        }
        
        # Overall status
        unhealthy_services = [name for name, service in services.items() 
                            if service["status"] != "healthy"]
        overall_status = "unhealthy" if unhealthy_services else "healthy"
        
        processing_time = time.time() - start_time
        
        return DetailedHealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="2.0.0",
            uptime=processing_time,
            services=services,
            system=system_info,
            performance=performance,
            dependencies=dependencies
        )
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/services/{service_name}")
async def check_specific_service(
    service_name: str,
    current_user: User = Depends(get_current_superuser)
) -> Dict[str, Any]:
    """
    Check health of a specific service.
    
    Provides detailed health information for individual services.
    """
    try:
        if service_name == "database":
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            return {
                "service": "database",
                "status": "healthy",
                "type": "SQLite" if "sqlite" in str(engine.url) else "PostgreSQL",
                "checked_at": datetime.utcnow().isoformat() + "Z"
            }
        
        elif service_name == "redis":
            redis_ping = await redis_service.ping()
            stats = await redis_service.get_cache_stats()
            return {
                "service": "redis",
                "status": "healthy" if redis_ping else "unhealthy",
                "stats": stats,
                "checked_at": datetime.utcnow().isoformat() + "Z"
            }
        
        elif service_name == "ollama":
            async with OllamaClient() as ollama:
                health = await ollama.health_check()
                model_info = await ollama.get_model_info()
                return {
                    "service": "ollama",
                    "status": health["status"],
                    "model": health.get("model"),
                    "response_time": health.get("response_time"),
                    "model_info": model_info,
                    "checked_at": datetime.utcnow().isoformat() + "Z"
                }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service check failed for {service_name}: {e}")
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat() + "Z"
        }