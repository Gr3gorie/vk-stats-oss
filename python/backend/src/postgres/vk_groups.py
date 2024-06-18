import asyncpg
import vk
from pydantic import BaseModel, TypeAdapter

# --------------------------------------------------------------------------------------------------


async def upsert_only_vk_data(
    pg_pool: asyncpg.Pool,
    *,
    groups: list[vk.groups.GroupById],
) -> None:
    async with pg_pool.acquire() as conn:
        for group in groups:
            await conn.execute(
                """
                    INSERT INTO vk_groups (
                        id, name, screen_name, members_count,
                        photo_50, photo_100, photo_200
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (id) DO UPDATE
                    SET name = EXCLUDED.name
                      , screen_name = EXCLUDED.screen_name
                      , members_count = EXCLUDED.members_count
                      , photo_50 = EXCLUDED.photo_50
                      , photo_100 = EXCLUDED.photo_100
                      , photo_200 = EXCLUDED.photo_200
                """,
                group.id,
                group.name,
                group.screen_name,
                group.members_count,
                group.photo_50,
                group.photo_100,
                group.photo_200,
            )


# --------------------------------------------------------------------------------------------------


class VkGroup(BaseModel):
    id: int
    name: str
    screen_name: str
    members_count: int
    photo_50: str | None = None
    photo_100: str | None = None
    photo_200: str | None = None


async def list_by_ids(
    pg_pool: asyncpg.Pool,
    *,
    group_ids: list[int],
) -> list[VkGroup]:
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT *
                FROM vk_groups
                WHERE id = ANY($1)
            """,
            group_ids,
        )

    return TypeAdapter(list[VkGroup]).validate_python(rows)
