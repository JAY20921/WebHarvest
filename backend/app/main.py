"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.database import init_db, close_db, get_db
from app.schemas.extraction import HealthResponse
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Intelligent Scraper API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Intelligent Scraper API...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Intelligent Scraper API",
    description="AI-Powered Web Data Extraction Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Scraper API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    Verifies that all critical services are operational
    """
    services = {"api": "ok"}
    
    # Check database connection
    try:
        await db.execute("SELECT 1")
        services["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "error"
    
    # Redis check will be added in Phase 8 with Celery
    # LLM provider checks will be added in Phase 5
    
    overall_status = "healthy" if all(v == "ok" for v in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        services=services
    )


# Additional routes will be imported here in future phases
# from app.api.routes import extraction, history, export
# app.include_router(extraction.router, prefix="/api", tags=["extraction"])
# app.include_router(history.router, prefix="/api", tags=["history"])
# app.include_router(export.router, prefix="/api", tags=["export"])
