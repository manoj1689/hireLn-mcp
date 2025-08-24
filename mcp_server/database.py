import asyncpg
import os

class Database:
    """Async Postgres database wrapper."""

    def __init__(self, pool):
        self.pool = pool

    @classmethod
    async def connect(cls):
        # Use DATABASE_URL env var or replace with your own connection string
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/hireln_db")
        pool = await asyncpg.create_pool(DATABASE_URL)
        return cls(pool)

    async def disconnect(self):
        await self.pool.close()

    async def query(self, sql: str):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql)
