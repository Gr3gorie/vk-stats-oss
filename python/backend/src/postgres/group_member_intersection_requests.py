from uuid import UUID

import asyncpg
from pydantic import BaseModel


class IntersectionRequestGroup(BaseModel):
    id: int
    name: str
    screen_name: str
    members_count: int
    photo_50: str | None = None
    photo_100: str | None = None
    photo_200: str | None = None


class IntersectionRequest(BaseModel):
    id: UUID
    user_id: int
    group_ids: list[int]
    update_job_ids: list[UUID]


async def select_by_id(
    pg_pool: asyncpg.Pool,
    *,
    request_id: UUID,
) -> IntersectionRequest | None:
    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT *
                FROM group_member_intersection_requests
                WHERE id = $1
            """,
            request_id,
        )

    if not row:
        return None

    return IntersectionRequest.model_validate(row)
