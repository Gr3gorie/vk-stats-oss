import traceback
from datetime import datetime
from uuid import UUID

import asyncpg
import structlog
import vk
from job import FailedJobInfo, JobStatus, RunningJobInfo, SucceededJobInfo
from pydantic import BaseModel, TypeAdapter
from utils import utc_now
from vk.errors import TransientError, with_transient_error_retry
from vk.groups.get_members import GetMembersRequest
from vk.groups.get_members_via_execute import GetMembersViaExecuteRequest

log = structlog.stdlib.get_logger()


class GroupUpdateJob(BaseModel):
    id: UUID
    group_id: int


async def group_update_job(
    vk_client: vk.Client,
    pg_pool: asyncpg.Pool,
    job: GroupUpdateJob,
):
    log.info("Updating group as running", job=job)
    await _update_job_as_running(pg_pool, job, progress=None)

    try:
        log.info("Starting group update job", job=job)
        await _do_job(vk_client, pg_pool, job)

        log.info("Updating group as succeeded", job=job)
        await _update_job_as_succeeded(pg_pool, job, completed_at=utc_now())
    except Exception as e:
        log.error("Job failed", exc_info=e)
        error = traceback.format_exc()
        await _update_job_as_failed(pg_pool, job, error=error, completed_at=utc_now())


async def _update_job_as_failed(
    pg_pool: asyncpg.Pool,
    job: GroupUpdateJob,
    *,
    error: str,
    completed_at: datetime,
):
    job_info = FailedJobInfo(
        type=JobStatus.Failed,
        error=error,
        completed_at=completed_at,
    )

    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                UPDATE group_update_jobs
                SET status = 'FAILED'
                  , info = $1::JSONB
                WHERE id = $2
            """,
            job_info,
            job.id,
        )


async def _update_job_as_running(
    pg_pool: asyncpg.Pool,
    job: GroupUpdateJob,
    *,
    progress: RunningJobInfo.Progress | None,
):
    job_info = RunningJobInfo(type=JobStatus.Running, progress=progress)

    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                UPDATE group_update_jobs
                SET status = 'RUNNING'
                  , info = $1::JSONB
                WHERE id = $2
            """,
            job_info,
            job.id,
        )


async def _update_job_as_succeeded(
    pg_pool: asyncpg.Pool,
    job: GroupUpdateJob,
    *,
    completed_at: datetime,
):
    job_info = SucceededJobInfo(
        type=JobStatus.Succeeded,
        completed_at=completed_at,
    )

    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                UPDATE group_update_jobs
                SET status = 'SUCCEEDED'
                  , info = $1::JSONB
                WHERE id = $2
            """,
            job_info,
            job.id,
        )


async def _do_job(
    vk_client: vk.Client,
    pg_pool: asyncpg.Pool,
    job: GroupUpdateJob,
) -> None:
    member_ids = []

    while True:
        offset = len(member_ids)
        log.info("Fetching group members", job=job, offset=offset)

        async def get_members(_error: TransientError | None):
            return await vk.groups.get_members_via_execute(
                vk_client,
                GetMembersViaExecuteRequest(
                    group_id=job.group_id,
                    offset=offset,
                ),
            )

        response = await with_transient_error_retry(get_members)
        if not response.member_ids:
            break

        member_ids.extend(response.member_ids)

        try:
            await _update_job_as_running(
                pg_pool,
                job,
                progress=RunningJobInfo.Progress(
                    num_updated=len(member_ids),
                    num_total=response.total_count,
                ),
            )
        except Exception as e:
            log.warn("Failed to update job as running, continuing...", job=job, error=e)

    log.info("Fetched group members", job=job, num_members=len(member_ids))

    log.info("Listing stale group members", job=job)
    stale_members = await _list_group_members(
        pg_pool,
        job.group_id,
    )

    left_members = set(stale_members) - set(member_ids)
    new_members = set(member_ids) - set(stale_members)

    async with pg_pool.acquire() as conn:
        async with conn.transaction():
            if left_members:
                await _remove_group_members(conn, job.group_id, list(left_members))
            else:
                log.info("No members left the group", job=job)

            if new_members:
                await _add_group_members(conn, job.group_id, list(new_members))
            else:
                log.info("No new members joined the group", job=job)

    await _update_group_last_updated_at(pg_pool, job.group_id)


async def _update_group_last_updated_at(
    pg_pool: asyncpg.Pool,
    group_id: int,
) -> None:
    log.info("Updating group last updated at", group_id=group_id)

    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
                UPDATE vk_groups
                SET last_updated_at = NOW()
                WHERE id = $1
            """,
            group_id,
        )


async def _remove_group_members(
    conn: asyncpg.Connection,
    group_id: int,
    user_ids: list[int],
) -> None:
    log.info("Removing group members", group_id=group_id, num_members=len(user_ids))

    await conn.execute(
        """
            DELETE FROM vk_group_members
            WHERE group_id = $1
              AND user_id = ANY($2)
        """,
        group_id,
        user_ids,
    )


async def _add_group_members(
    conn: asyncpg.Connection,
    group_id: int,
    user_ids: list[int],
) -> None:
    log.info("Adding group members", group_id=group_id, num_members=len(user_ids))

    await conn.executemany(
        """
            INSERT INTO vk_group_members (group_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT (group_id, user_id) DO NOTHING
        """,
        [(group_id, user_id) for user_id in user_ids],
    )


async def _list_group_members(
    pg_pool: asyncpg.Pool,
    group_id: int,
) -> list[int]:
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT user_id
                FROM vk_group_members
                WHERE group_id = $1
            """,
            group_id,
        )

    return TypeAdapter(list[int]).validate_python([row["user_id"] for row in rows])


async def get_num_total_members(
    vk_client: vk.Client,
    group_id: int,
) -> int:
    response = await vk.groups.get_members(
        vk_client,
        GetMembersRequest(
            group_id=group_id,
            count=1,
        ),
    )
    return response.count
