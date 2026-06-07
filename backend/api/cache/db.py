"""PostgreSQL 캐싱 레이어 — API 응답 24시간 캐싱 (DB 없으면 no-op)"""
import os
import hashlib
import json
from datetime import datetime, timedelta, timezone

DATABASE_URL = os.environ.get("POSTGRES_URL", "")

_pool = None
_db_available = None  # None=미확인, True=가능, False=불가


async def get_pool():
    global _pool, _db_available
    if _db_available is False:
        return None
    if _pool is None:
        if not DATABASE_URL or "user:password@host" in DATABASE_URL:
            _db_available = False
            return None
        try:
            import asyncpg
            _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
            await init_db(_pool)
            _db_available = True
        except Exception:
            _db_available = False
            return None
    return _pool


async def init_db(pool):
    """캐시 테이블 생성"""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cache_key VARCHAR(255) UNIQUE NOT NULL,
                request_data JSONB NOT NULL,
                response_data JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_key ON api_cache(cache_key)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at)
        """)


def make_cache_key(address: str, rental_type: str, deposit: int, monthly_rent: int | None) -> str:
    """캐시 키 생성: 주소+금액+타입 해시"""
    raw = f"{address}|{rental_type}|{deposit}|{monthly_rent or 0}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_cached(key: str) -> dict | None:
    """캐시된 응답 조회"""
    pool = await get_pool()
    if pool is None:
        return None

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT response_data FROM api_cache WHERE cache_key = $1 AND expires_at > NOW()",
            key,
        )
        if row:
            return json.loads(row["response_data"])
    return None


async def set_cached(key: str, request_data: dict, response_data: dict, ttl_hours: int = 24):
    """응답 캐싱"""
    pool = await get_pool()
    if pool is None:
        return

    expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO api_cache (cache_key, request_data, response_data, expires_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (cache_key) DO UPDATE SET
                request_data = $2,
                response_data = $3,
                created_at = NOW(),
                expires_at = $4
            """,
            key,
            json.dumps(request_data, ensure_ascii=False),
            json.dumps(response_data, ensure_ascii=False),
            expires_at,
        )


async def cleanup_expired():
    """만료된 캐시 정리"""
    pool = await get_pool()
    if pool is None:
        return

    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM api_cache WHERE expires_at < NOW()")
