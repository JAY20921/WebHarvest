"""
Database Connection and Base Configuration
"""

from typing import Any, Dict, Tuple

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# libpq-style query params that asyncpg does not understand
_UNSUPPORTED_ASYNCPG_PARAMS = {"sslmode", "channel_binding", "sslrootcert", "sslcert", "sslkey", "options"}


def build_async_database_url(raw_url: str) -> Tuple[str, Dict[str, Any]]:
    """
    Convert a standard Postgres URL (as given by Neon, Supabase, Railway, RDS...)
    into an asyncpg URL plus connect_args.

    - postgres:// / postgresql:// -> postgresql+asyncpg://
    - ?sslmode=require (libpq) -> connect_args={"ssl": "require"} (asyncpg)
    - strips other libpq-only params such as channel_binding
    """
    url = make_url(raw_url)
    if url.drivername in ("postgres", "postgresql", "postgresql+psycopg2"):
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    connect_args: Dict[str, Any] = {}

    sslmode = query.get("sslmode") or query.get("ssl")
    if sslmode and sslmode != "disable":
        # asyncpg accepts libpq-style mode names for ssl
        connect_args["ssl"] = sslmode if sslmode in ("require", "verify-ca", "verify-full", "prefer", "allow") else "require"

    for key in list(query):
        if key in _UNSUPPORTED_ASYNCPG_PARAMS or key == "ssl":
            query.pop(key)

    url = url.set(query=query)

    # PgBouncer in transaction mode (Supabase pooler :6543, Neon "-pooler" hosts)
    # breaks asyncpg prepared statements unless the statement cache is disabled.
    host = url.host or ""
    if url.port == 6543 or "-pooler" in host or "pooler." in host:
        connect_args["statement_cache_size"] = 0

    return url.render_as_string(hide_password=False), connect_args


DATABASE_URL, _connect_args = build_async_database_url(settings.DATABASE_URL)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using (cloud DBs drop idle conns)
    pool_recycle=300,  # Serverless DBs (e.g. Neon) close idle connections
    connect_args=_connect_args,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session
    Usage in FastAPI routes:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
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


async def init_db():
    """
    Initialize database (create tables)
    This will be called on application startup
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from app.models.extraction import ExtractionJob  # noqa
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    This will be called on application shutdown
    """
    await engine.dispose()
