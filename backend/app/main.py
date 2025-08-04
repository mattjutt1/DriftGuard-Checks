"""
PromptEvolver FastAPI Backend Application.

A robust, scalable backend API for prompt optimization using Microsoft PromptWizard
framework with Ollama integration, background processing, and Redis caching.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

from .api.v1 import api_router
from .core.config import settings
from .db.session import engine
from .db.base import Base
from .services.redis_service import redis_service
from .services.celery_app import celery_app

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
OPTIMIZATION_COUNT = Counter('optimization_requests_total', 'Total optimization requests', ['status'])
OPTIMIZATION_DURATION = Histogram('optimization_duration_seconds', 'Optimization processing time')


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.observe(time.time() - start_time)
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        await logger.ainfo(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        try:
            response = await call_next(request)
            
            # Log successful response
            duration = time.time() - start_time
            await logger.ainfo(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            await logger.aerror(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration=duration,
            )
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    
    # Startup
    logger.info("Starting PromptEvolver backend...")
    
    try:
        # Initialize database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
        
        # Initialize Redis connection
        await redis_service.initialize()
        logger.info("Redis connection established")
        
        # Test Ollama connection
        from .services.ollama_client import OllamaClient
        async with OllamaClient() as ollama:
            health = await ollama.health_check()
            if health["status"] == "healthy":
                logger.info("Ollama connection established", model=health["model"])
            else:
                logger.warning("Ollama health check failed", error=health.get("error"))
        
        logger.info("PromptEvolver backend started successfully")
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down PromptEvolver backend...")
    
    try:
        # Close Redis connection
        await redis_service.close()
        logger.info("Redis connection closed")
        
        # Close database connections
        await engine.dispose()
        logger.info("Database connections closed")
        
        logger.info("PromptEvolver backend shutdown complete")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered prompt optimization platform using Microsoft PromptWizard",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    
    # Custom middleware
    if settings.PROMETHEUS_ENABLED:
        app.add_middleware(PrometheusMiddleware)
    
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        try:
            # Check Redis connection
            redis_status = await redis_service.ping()
            
            # Check database connection
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            db_status = True
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": settings.APP_VERSION,
                "services": {
                    "redis": "healthy" if redis_status else "unhealthy",
                    "database": "healthy" if db_status else "unhealthy",
                }
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": time.time(),
                    "error": str(e)
                }
            )
    
    # Metrics endpoint for Prometheus
    if settings.PROMETHEUS_ENABLED:
        @app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Global HTTP exception handler with structured logging."""
        await logger.aerror(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            url=str(request.url),
            method=request.method,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "timestamp": time.time(),
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled exceptions."""
        await logger.aerror(
            "Unhandled exception",
            error=str(exc),
            url=str(request.url),
            method=request.method,
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "timestamp": time.time(),
                }
            }
        )
    
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )