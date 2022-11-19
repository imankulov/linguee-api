import pathlib
from typing import Optional

import aiosqlite

from linguee_api.downloaders.interfaces import ICache, IDownloader


class SQLiteCache(ICache):
    """SQLite Cache."""

    def __init__(self, cache_database: pathlib.Path, upstream: IDownloader):
        self.cache_database = cache_database
        self.upstream = upstream

    async def get_from_cache(self, url: str) -> Optional[str]:
        await self._ensure_database_initialized()
        async with aiosqlite.connect(self.cache_database) as db:
            async with db.execute(
                "SELECT page FROM cache WHERE url = ?", [url]
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
        return row[0]

    async def put_to_cache(self, url: str, page: str) -> None:
        async with aiosqlite.connect(self.cache_database) as db:
            await db.execute("INSERT INTO cache (url, page) VALUES (?, ?)", [url, page])
            await db.commit()

    async def _ensure_database_initialized(self):
        if self.cache_database.is_file():
            return
        self.cache_database.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.cache_database) as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS cache (
                    url TEXT PRIMARY KEY,
                    page TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            await db.commit()
