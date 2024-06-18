from datetime import datetime

import asyncpg
from fastapi import HTTPException
from pydantic import AnyHttpUrl, BaseModel, TypeAdapter

from api.auth.cookie import AuthCookieValueExtractor
from api.state import ApiStateExtractor


class GroupLastUpdated(BaseModel):
    last_updated_at: datetime | None


async def get_last_updated(
    state: ApiStateExtractor,
    _auth: AuthCookieValueExtractor,
    group_url: AnyHttpUrl,
) -> GroupLastUpdated:
    screen_name = _parse_screen_name(group_url)

    last_updated_at = await _select_group_last_updated_at(
        state.pg_pool,
        screen_name,
    )

    return GroupLastUpdated(last_updated_at=last_updated_at)


async def _select_group_last_updated_at(
    pg_pool: asyncpg.Pool,
    screen_name: str,
) -> datetime | None:
    async with pg_pool.acquire() as conn:
        last_updated_at = await conn.fetchval(
            """
                SELECT last_updated_at
                FROM vk_groups
                WHERE screen_name = $1
            """,
            screen_name,
        )

    if last_updated_at is None:
        return None

    return TypeAdapter(datetime).validate_python(last_updated_at)


def _parse_screen_name(url: AnyHttpUrl) -> str:
    if url.host != "vk.com":
        raise HTTPException(status_code=400, detail="Only VK urls are supported")

    path = (url.path or "").strip("/")
    if not path:
        raise HTTPException(status_code=400, detail="Empty path")

    parts = path.split("/")
    if not parts:
        raise HTTPException(status_code=400, detail="Empty path")

    return parts[0]
