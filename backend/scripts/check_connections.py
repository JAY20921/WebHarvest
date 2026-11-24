"""
Connectivity check for cloud services.

Usage (from the backend/ folder, with the venv active):
    python -m scripts.check_connections

Checks: PostgreSQL (DATABASE_URL), Redis (REDIS_URL / CELERY_BROKER_URL),
and that LLM API keys are present. Never prints secrets.
"""

import asyncio
import sys
from urllib.parse import urlparse

from sqlalchemy import text


def _host(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.hostname}:{parsed.port or ''}{parsed.path}"


async def check_postgres() -> bool:
    from app.core.config import settings
    from app.models.database import engine, init_db

    print(f"[postgres] {_host(settings.DATABASE_URL)}")
    try:
        async with engine.connect() as conn:
            version = (await conn.execute(text("SELECT version()"))).scalar_one()
        print(f"  OK  connected: {version.split(',')[0]}")
        await init_db()
        print("  OK  tables created / verified")
        return True
    except Exception as e:  # noqa: BLE001 - diagnostic script
        print(f"  FAIL {type(e).__name__}: {e}")
        return False
    finally:
        await engine.dispose()


def check_redis() -> bool:
    import redis
    from app.core.config import settings

    ok = True
    for name in ("REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"):
        url = getattr(settings, name)
        print(f"[redis] {name} = {_host(url)}")
        try:
            client = redis.Redis.from_url(url, socket_timeout=10)
            client.ping()
            print("  OK  ping")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL {type(e).__name__}: {e}")
            ok = False
    return ok


def check_llm_keys() -> bool:
    from app.core.config import settings

    ok = True
    for name in ("GROQ_API_KEY", "GEMINI_API_KEY"):
        value = getattr(settings, name)
        placeholder = not value or value.startswith("your_")
        print(f"[llm] {name}: {'MISSING' if placeholder else 'set'}")
        ok = ok and not placeholder
    return ok


def main() -> int:
    results = {
        "postgres": asyncio.run(check_postgres()),
        "redis": check_redis(),
        "llm_keys": check_llm_keys(),
    }
    print("\nSummary:", ", ".join(f"{k}={'OK' if v else 'FAIL'}" for k, v in results.items()))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
