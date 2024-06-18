import asyncpg
from pydantic import TypeAdapter, ValidationError


async def select_access_token(pg_pool: asyncpg.Pool, *, user_id: int) -> str | None:
    async with pg_pool.acquire() as conn:
        token = await conn.fetchval(
            """
                SELECT access_token
                FROM vk_oauth_tokens
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """,
            user_id,
        )

    try:
        return TypeAdapter(str).validate_python(token)
    except ValidationError:
        return None
