import asyncio
from typing import Annotated, Literal
from uuid import UUID, uuid4

import asyncpg
import postgres
import structlog
import vk
from fastapi import HTTPException
from job import JobInfo, JobStatus
from pydantic import BaseModel, Field
from vk.errors import TransientError, with_transient_error_retry
from vk.groups.get_by_id import GetByIdRequest
from vk.pagination import VK_PAGINATION_MAX_ITEMS
from vk.users.get_via_execute import GetUsersViaExecuteRequest
from vk_extra import VkGroupUrl

from api.auth.cookie import AuthCookieValueExtractor
from api.state import ApiStateExtractor

from .build_portrait import AveragePortrait, build_portrait

log = structlog.stdlib.get_logger()

# --------------------------------------------------------------------------------------------------

MIN_NUM_GROUPS = 1
MAX_NUM_GROUPS = 10


class UsersAveragePortrait_Request:
    class Request(BaseModel):
        class Group(BaseModel):
            url: VkGroupUrl
            freshness: Literal["FRESH", "STALE"]

        groups: list[Group]

    class Error:
        class ReachedLimits(BaseModel):
            type: Literal["REACHED_LIMITS"]
            min_num_groups: int
            max_num_groups: int

        class UserMissingAccessToken(BaseModel):
            type: Literal["MISSING_ACCESS_TOKEN"]

        class InvalidGroupUrls(BaseModel):
            class InvalidGroupUrl(BaseModel):
                url: str
                index: int

            type: Literal["INVALID_GROUP_URLS"]
            urls: list[InvalidGroupUrl]

    class Info(BaseModel):
        type: Literal["INFO"]
        request_id: UUID

    Result = Annotated[
        Info
        | Error.ReachedLimits
        | Error.UserMissingAccessToken
        | Error.InvalidGroupUrls,
        # | GroupsMemberIntersectionDuplicateGroups
        # | GroupsMemberIntersectionInfo
        Field(..., discriminator="type"),
    ]


async def request_average_portrait(
    state: ApiStateExtractor,
    auth: AuthCookieValueExtractor,
    request: UsersAveragePortrait_Request.Request,
) -> UsersAveragePortrait_Request.Result:
    group_screen_names = list(set(group.url.screen_name for group in request.groups))
    if len(group_screen_names) < MIN_NUM_GROUPS:
        return UsersAveragePortrait_Request.Error.ReachedLimits(
            type="REACHED_LIMITS",
            min_num_groups=MIN_NUM_GROUPS,
            max_num_groups=MAX_NUM_GROUPS,
        )
    if len(group_screen_names) > MAX_NUM_GROUPS:
        return UsersAveragePortrait_Request.Error.ReachedLimits(
            type="REACHED_LIMITS",
            min_num_groups=MIN_NUM_GROUPS,
            max_num_groups=MAX_NUM_GROUPS,
        )

    user_access_token = await postgres.vk_oauth_tokens.select_access_token(
        state.pg_pool,
        user_id=auth.user_id,
    )
    if not user_access_token:
        return UsersAveragePortrait_Request.Error.UserMissingAccessToken(
            type="MISSING_ACCESS_TOKEN"
        )
    user_vk_client = state.vk_client.with_new_access_token(user_access_token)

    async def get_groups_by_screen_names(_error: TransientError | None):
        return await vk.groups.get_by_id(
            user_vk_client,
            GetByIdRequest(group_ids=",".join(group_screen_names)),
        )

    log.info("Getting groups by screen names...")
    response = await with_transient_error_retry(get_groups_by_screen_names)
    if len(group_screen_names) != len(response.groups):
        log.debug(
            "Missing groups after resolving screen names",
            group_screen_names=group_screen_names,
            response_groups=response.groups,
        )
        missing_screen_names = set(group_screen_names) - {
            group.screen_name for group in response.groups
        }
        return UsersAveragePortrait_Request.Error.InvalidGroupUrls(
            type="INVALID_GROUP_URLS",
            urls=[
                UsersAveragePortrait_Request.Error.InvalidGroupUrls.InvalidGroupUrl(
                    url=f"https://vk.com/{screen_name}",
                    index=group_screen_names.index(screen_name),
                )
                for screen_name in missing_screen_names
            ],
        )
    log.info("Got groups by screen names", group_ids=[g.id for g in response.groups])

    log.info("Upserting groups...")
    await postgres.vk_groups.upsert_only_vk_data(state.pg_pool, groups=response.groups)

    portrait_request_id = uuid4()
    group_ids_to_update = [
        group.id
        for group, g in zip(response.groups, request.groups)
        if g.freshness == "FRESH"
    ]
    log.info("Inserting group update jobs...", group_ids=group_ids_to_update)
    job_ids = await postgres.group_update_jobs.insert_many(
        state.pg_pool,
        request_id=portrait_request_id,
        user_id=auth.user_id,
        group_ids=group_ids_to_update,
    )

    log.info(
        "Inserting user average portrait request...",
        request_id=portrait_request_id,
    )
    await _insert_user_average_portrait_request(
        state.pg_pool,
        request_id=portrait_request_id,
        user_id=auth.user_id,
        group_ids=[group.id for group in response.groups],
        update_job_ids=job_ids,
    )

    log.info("Done", request_id=portrait_request_id)
    return UsersAveragePortrait_Request.Info(
        type="INFO",
        request_id=portrait_request_id,
    )


async def _insert_user_average_portrait_request(
    pg_pool: asyncpg.Pool,
    request_id: UUID,
    user_id: int,
    group_ids: list[int],
    update_job_ids: list[UUID],
) -> None:
    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                INSERT INTO user_average_portrait_requests (
                    id, user_id, group_ids, update_job_ids
                )
                VALUES ($1, $2, $3, $4)
            """,
            request_id,
            user_id,
            group_ids,
            update_job_ids,
        )


# --------------------------------------------------------------------------------------------------


class UsersAveragePortrait_View:
    class Response(BaseModel):
        class Group(BaseModel):
            id: int
            name: str
            screen_name: str
            members_count: int
            photo_url: str | None = None

        class GroupUpdateJob(BaseModel):
            group_id: int
            status: JobStatus
            info: JobInfo

        groups: list[Group]
        update_jobs: list[GroupUpdateJob]
        num_total_users: int
        average_portrait: AveragePortrait | None


async def view_average_portrait_request(
    state: ApiStateExtractor,
    auth: AuthCookieValueExtractor,
    request_id: UUID,
) -> UsersAveragePortrait_View.Response:
    request = await _select_user_average_portrait_request(
        state.pg_pool,
        request_id=request_id,
    )
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    groups, update_jobs = await asyncio.gather(
        postgres.vk_groups.list_by_ids(state.pg_pool, group_ids=request.group_ids),
        postgres.group_update_jobs.list_by_ids(
            state.pg_pool,
            job_ids=request.update_job_ids,
        ),
    )
    groups.sort(key=lambda g: g.name.lower())
    update_jobs.sort(key=lambda j: j.created_at)

    response_groups = [
        UsersAveragePortrait_View.Response.Group(
            id=group.id,
            name=group.name,
            screen_name=group.screen_name,
            members_count=group.members_count,
            photo_url=group.photo_200 or group.photo_100 or group.photo_50,
        )
        for group in groups
    ]
    response_update_jobs = [
        UsersAveragePortrait_View.Response.GroupUpdateJob(
            group_id=job.group_id,
            status=job.status,
            info=job.info,
        )
        for job in update_jobs
    ]

    has_uncompleted_jobs = any(not job.status.is_completed() for job in update_jobs)
    if has_uncompleted_jobs:
        return UsersAveragePortrait_View.Response(
            groups=response_groups,
            update_jobs=response_update_jobs,
            num_total_users=0,
            average_portrait=None,
        )

    user_access_token = await postgres.vk_oauth_tokens.select_access_token(
        state.pg_pool,
        user_id=auth.user_id,
    )
    if not user_access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_vk_client = state.vk_client.with_new_access_token(user_access_token)

    all_users = await _get_all_users(
        state.pg_pool,
        user_vk_client,
        group_ids=request.group_ids,
    )
    log.info("Got all users", num_users=len(all_users))

    average_portrait = build_portrait(all_users)

    return UsersAveragePortrait_View.Response(
        groups=response_groups,
        update_jobs=response_update_jobs,
        num_total_users=len(all_users),
        average_portrait=average_portrait,
    )


async def _get_all_users(
    pg_pool: asyncpg.Pool,
    vk_client: vk.Client,
    *,
    group_ids: list[int],
) -> list[vk.users.User]:
    all_users: list[vk.users.User] = []

    log.info("Getting all users...", group_ids=group_ids)

    for i, group_id in enumerate(group_ids):
        log.info(
            "Fetching group members",
            group_id=group_id,
            progress=f"{i+1}/{len(group_ids)}",
        )
        group_member_ids = await postgres.vk_group_members.list_by_group_id(
            pg_pool,
            group_id=group_id,
        )

        group_users: list[vk.users.User] = []
        limit = 8 * VK_PAGINATION_MAX_ITEMS

        for i in range(0, len(group_member_ids), limit):
            batch = group_member_ids[i : i + limit]
            batch_ids = [m.user_id for m in batch]

            # TODO: Try `users.get` without `execute`.
            async def get_users(_error: TransientError | None):
                return await vk.users.get_users_via_execute(
                    vk_client, GetUsersViaExecuteRequest(user_ids=batch_ids)
                )

            log.info(
                "Fetching group users via execute",
                group_id=group_id,
                offset=i,
                num_users=len(batch_ids),
            )
            response = await with_transient_error_retry(get_users)
            if not response.users:
                break

            group_users.extend(response.users)

        log.info("Fetched group users", group_id=group_id, num_users=len(group_users))
        all_users.extend(group_users)

    return all_users


class AveragePortraitRequest(BaseModel):
    id: UUID
    group_ids: list[int]
    update_job_ids: list[UUID]


async def _select_user_average_portrait_request(
    pg_pool: asyncpg.Pool,
    *,
    request_id: UUID,
) -> AveragePortraitRequest | None:
    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
                SELECT *
                FROM user_average_portrait_requests
                WHERE id = $1
            """,
            request_id,
        )

    if not row:
        return None

    return AveragePortraitRequest.model_validate(row)
