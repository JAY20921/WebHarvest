"""
FastAPI Dependencies
Reusable dependency functions for API routes
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Yields:
        AsyncSession instance
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
