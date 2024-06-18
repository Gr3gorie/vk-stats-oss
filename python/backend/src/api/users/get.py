from typing import Annotated, Literal
from uuid import UUID

import asyncpg
import postgres
import structlog
import vk
from fastapi import HTTPException
from pydantic import BaseModel, Field, TypeAdapter
from vk.errors import TransientError, with_transient_error_retry
from vk.pagination import VK_PAGINATION_MAX_ITEMS
from vk.users.get import User
from vk.users.get_via_execute import GetUsersViaExecuteRequest

from api.auth.cookie import AuthCookieValueExtractor
from api.state import ApiStateExtractor

log = structlog.stdlib.get_logger()


class GetUsers:
    class FromGroupMemberIntersection(BaseModel):
        type: Literal["FROM_GROUP_MEMBER_INTERSECTION"]
        request_id: UUID

    Request = Annotated[
        FromGroupMemberIntersection,
        Field(..., discriminator="type"),
    ]


async def get_users(
    state: ApiStateExtractor,
    auth: AuthCookieValueExtractor,
    request: GetUsers.Request,
) -> list[User]:
    match request.type:
        case "FROM_GROUP_MEMBER_INTERSECTION":
            intersection_request = (
                await postgres.group_member_intersection_requests.select_by_id(
                    state.pg_pool,
                    request_id=request.request_id,
                )
            )
            if not intersection_request:
                raise HTTPException(status_code=404, detail="Request not found")
            if intersection_request.user_id != auth.user_id:
                raise HTTPException(status_code=403, detail="Forbidden")

            user_access_token = await postgres.vk_oauth_tokens.select_access_token(
                state.pg_pool,
                user_id=auth.user_id,
            )
            if not user_access_token:
                raise HTTPException(status_code=401, detail="Unauthorized")
            user_vk_client = state.vk_client.with_new_access_token(user_access_token)

            intersection_member_ids = await _list_intersection_member_ids(
                state.pg_pool,
                group_ids=intersection_request.group_ids,
            )
            return await _get_all_users(
                user_vk_client,
                user_ids=intersection_member_ids,
            )


async def _list_intersection_member_ids(
    pg_pool: asyncpg.Pool,
    *,
    group_ids: list[int],
) -> list[int]:
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
                WITH users_with_group_counts AS (
                    SELECT user_id
                         , COUNT(DISTINCT group_id) AS group_count
                    FROM vk_group_members
                    WHERE group_id = ANY($1)
                    GROUP BY user_id
                )

                SELECT user_id
                FROM users_with_group_counts
                WHERE group_count = $2
            """,
            group_ids,
            len(group_ids),
        )

    return TypeAdapter(list[int]).validate_python([row["user_id"] for row in rows])


async def _get_all_users(
    vk_client: vk.Client,
    *,
    user_ids: list[int],
) -> list[vk.users.User]:
    all_users: list[vk.users.User] = []

    log.info("Getting all users...", num_users=len(user_ids))

    limit = 8 * VK_PAGINATION_MAX_ITEMS

    for i in range(0, len(user_ids), limit):
        batch_ids = user_ids[i : i + limit]

        # TODO: Try `users.get` without `execute`.
        async def get_users(_error: TransientError | None):
            return await vk.users.get_users_via_execute(
                vk_client, GetUsersViaExecuteRequest(user_ids=batch_ids)
            )

        log.info(
            "Fetching users via execute",
            offset=i,
            num_users=len(batch_ids),
        )
        response = await with_transient_error_retry(get_users)
        if not response.users:
            break

        all_users.extend(response.users)

    return all_users
