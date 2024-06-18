import asyncio
from typing import Annotated, Literal
from uuid import UUID, uuid4

import postgres
import structlog
import vk
from asyncpg.connection import asyncpg
from fastapi import HTTPException
from job import JobInfo, JobStatus
from pydantic import BaseModel, Field, TypeAdapter
from vk.errors import TransientError, with_transient_error_retry
from vk.groups.get_by_id import GetByIdRequest
from vk_extra import VkGroupUrl

from api.auth.cookie import AuthCookieValueExtractor
from api.state import ApiStateExtractor

log = structlog.stdlib.get_logger()

# --------------------------------------------------------------------------------------------------

MIN_NUM_GROUPS = 2
MAX_NUM_GROUPS = 10


class GroupToIntersect(BaseModel):
    url: VkGroupUrl
    freshness: Literal["FRESH", "STALE"]


class GroupsMemberIntersectionRequest(BaseModel):
    groups: list[GroupToIntersect]


class InvalidGroupUrl(BaseModel):
    url: str
    index: int
    reason: Literal["NOT_VK", "MISSING_GROUP", "FAILED_TO_RESOLVE", "NOT_GROUP"]


class GroupsMemberIntersectionInvalidUrls(BaseModel):
    type: Literal["INVALID_URLS"]
    invalid_urls: list[InvalidGroupUrl]


class GroupsMemberIntersectionReachedLimits(BaseModel):
    type: Literal["REACHED_LIMITS"]
    min_num_groups: int
    max_num_groups: int


class GroupsMemberIntersectionDuplicateGroups(BaseModel):
    type: Literal["DUPLICATE_GROUPS"]
    # duplicate_groups: list[str]


class GroupsMemberIntersectionInfo(BaseModel):
    type: Literal["INFO"]
    request_id: UUID


class UserMissingAccessToken(BaseModel):
    type: Literal["MISSING_ACCESS_TOKEN"]


GroupsMemberIntersectionResult = Annotated[
    GroupsMemberIntersectionInvalidUrls
    | GroupsMemberIntersectionReachedLimits
    | GroupsMemberIntersectionDuplicateGroups
    | GroupsMemberIntersectionInfo
    | UserMissingAccessToken,
    Field(..., discriminator="type"),
]


# TODO: Add check for size of the groups. Must be less than 500k.
async def request_member_intersection(
    state: ApiStateExtractor,
    auth: AuthCookieValueExtractor,
    request: GroupsMemberIntersectionRequest,
) -> GroupsMemberIntersectionResult:
    group_screen_names = list(set(group.url.screen_name for group in request.groups))
    if len(group_screen_names) < MIN_NUM_GROUPS:
        return GroupsMemberIntersectionReachedLimits(
            type="REACHED_LIMITS",
            min_num_groups=MIN_NUM_GROUPS,
            max_num_groups=MAX_NUM_GROUPS,
        )
    if len(group_screen_names) > MAX_NUM_GROUPS:
        return GroupsMemberIntersectionReachedLimits(
            type="REACHED_LIMITS",
            min_num_groups=MIN_NUM_GROUPS,
            max_num_groups=MAX_NUM_GROUPS,
        )

    user_access_token = await postgres.vk_oauth_tokens.select_access_token(
        state.pg_pool,
        user_id=auth.user_id,
    )
    if not user_access_token:
        return UserMissingAccessToken(type="MISSING_ACCESS_TOKEN")
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
        return GroupsMemberIntersectionInvalidUrls(
            type="INVALID_URLS",
            invalid_urls=[
                InvalidGroupUrl(
                    url=f"https://vk.com/{screen_name}",
                    index=group_screen_names.index(screen_name),
                    reason="NOT_GROUP",
                )
                for screen_name in missing_screen_names
            ],
        )
    log.info("Got groups by screen names", group_ids=[g.id for g in response.groups])

    log.info("Upserting groups...")
    await postgres.vk_groups.upsert_only_vk_data(state.pg_pool, groups=response.groups)

    intersection_request_id = uuid4()
    group_ids_to_update = [
        group.id
        for group, g in zip(response.groups, request.groups)
        if g.freshness == "FRESH"
    ]
    log.info("Inserting group update jobs...", group_ids=group_ids_to_update)
    job_ids = await postgres.group_update_jobs.insert_many(
        state.pg_pool,
        request_id=intersection_request_id,
        user_id=auth.user_id,
        group_ids=group_ids_to_update,
    )

    log.info(
        "Inserting group member intersection request...",
        request_id=intersection_request_id,
    )
    await _insert_group_member_intersection_request(
        state.pg_pool,
        request_id=intersection_request_id,
        user_id=auth.user_id,
        group_ids=[group.id for group in response.groups],
        update_job_ids=job_ids,
    )

    log.info("Done", request_id=intersection_request_id)
    return GroupsMemberIntersectionInfo(
        type="INFO",
        request_id=intersection_request_id,
    )


async def _insert_group_member_intersection_request(
    pg_pool: asyncpg.Pool,
    *,
    request_id: UUID,
    user_id: int,
    group_ids: list[int],
    update_job_ids: list[UUID],
) -> None:
    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                INSERT INTO group_member_intersection_requests (
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


class GroupsViewMemberIntersectionResponse(BaseModel):
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
    intersection_member_ids: list[int]


async def view_member_intersection_request(
    state: ApiStateExtractor,
    _auth: AuthCookieValueExtractor,
    request_id: UUID,
) -> GroupsViewMemberIntersectionResponse:
    request = await postgres.group_member_intersection_requests.select_by_id(
        state.pg_pool,
        request_id=request_id,
    )
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    groups, update_jobs, intersection_member_ids = await asyncio.gather(
        postgres.vk_groups.list_by_ids(state.pg_pool, group_ids=request.group_ids),
        postgres.group_update_jobs.list_by_ids(
            state.pg_pool, job_ids=request.update_job_ids
        ),
        _list_intersection_member_ids(state.pg_pool, group_ids=request.group_ids),
    )
    groups.sort(key=lambda g: g.name.lower())
    update_jobs.sort(key=lambda j: j.created_at)

    response_groups = [
        GroupsViewMemberIntersectionResponse.Group(
            id=group.id,
            name=group.name,
            screen_name=group.screen_name,
            members_count=group.members_count,
            photo_url=group.photo_200 or group.photo_100 or group.photo_50,
        )
        for group in groups
    ]
    response_update_jobs = [
        GroupsViewMemberIntersectionResponse.GroupUpdateJob(
            group_id=job.group_id,
            status=job.status,
            info=job.info,
        )
        for job in update_jobs
    ]
    return GroupsViewMemberIntersectionResponse(
        groups=response_groups,
        update_jobs=response_update_jobs,
        intersection_member_ids=intersection_member_ids,
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
