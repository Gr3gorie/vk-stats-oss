import asyncpg
from pydantic import BaseModel, TypeAdapter


class VkGroupMember(BaseModel):
    user_id: int


async def list_by_group_id(
    pg_pool: asyncpg.Pool,
    *,
    group_id: int,
) -> list[VkGroupMember]:
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT user_id
                FROM vk_group_members
                WHERE group_id = $1
            """,
            group_id,
        )

    return TypeAdapter(list[VkGroupMember]).validate_python(rows)
