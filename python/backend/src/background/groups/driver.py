import asyncio
from collections.abc import Mapping
from uuid import UUID

import asyncpg
import httpx
import structlog
import vk
from job import JobInfo, JobStatus
from pydantic import BaseModel, TypeAdapter, ValidationError

from .update_job import GroupUpdateJob, group_update_job

log = structlog.stdlib.get_logger()


async def drive_update_jobs(
    pg_pool: asyncpg.Pool,
    http_client: httpx.AsyncClient,
    *,
    drive_every_n_seconds: float = 5,
):
    log.info("Starting group update driver...")

    # this tells python that asyncpg.Record is a subclass of Mapping,
    # meaning the isinstance check within Pydantic will pass
    Mapping.register(asyncpg.Record)  # type: ignore

    while True:
        try:
            log.debug("Driving group update jobs...")
            await _drive_once(pg_pool, http_client)
        except Exception as e:
            log.error("Failed to drive group update jobs", exc_info=e)

        await asyncio.sleep(drive_every_n_seconds)


async def _drive_once(
    pg_pool: asyncpg.Pool,
    http_client: httpx.AsyncClient,
):
    user_jobs = await _list_oldest_one_job_per_user(pg_pool)

    for job in user_jobs.invalid_jobs:
        log.error("Invalid job", job=job)

    for job in user_jobs.valid_jobs:
        if job.status == JobStatus.Running:
            log.debug("Skipping running group update job", job=job)
            continue

        access_token = await _select_user_access_token(pg_pool, user_id=job.user_id)
        if not access_token:
            log.error("Failed to get user access token", job=job)
            continue

        log.info("Starting group update job", job=job)
        user_vk_client = vk.Client(http_client, access_token=access_token)
        asyncio.create_task(
            group_update_job(
                user_vk_client,
                pg_pool,
                GroupUpdateJob(
                    id=job.id,
                    group_id=job.group_id,
                ),
            )
        )


async def _select_user_access_token(
    pg_pool: asyncpg.Pool,
    *,
    user_id: int,
) -> str | None:
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


class UserJob(BaseModel):
    id: UUID
    user_id: int
    group_id: int
    status: JobStatus
    info: JobInfo


class JobsByUser(BaseModel):
    valid_jobs: list[UserJob]
    invalid_jobs: list[UserJob]


async def _list_oldest_one_job_per_user(
    pg_pool: asyncpg.Pool,
    *,
    limit: int = 5,
) -> JobsByUser:
    async with pg_pool.acquire() as conn:
        async with conn.transaction():
            rows = await conn.fetch(
                """
                    WITH ranked_jobs AS (
                        SELECT id
                             , user_id
                             , group_id
                             , status
                             , info
                             , ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at ASC) AS rn
                        FROM group_update_jobs
                        WHERE status IN ('PENDING', 'RUNNING')
                    )

                    SELECT g.id
                         , g.user_id
                         , g.group_id
                         , g.status
                         , g.info::JSONB

                    FROM group_update_jobs g
                    JOIN ranked_jobs r
                        ON g.id = r.id

                    WHERE r.rn = 1
                    LIMIT $1

                    FOR UPDATE
                """,
                limit,
            )

    log.debug("Fetched oldest one job per user", rows=rows)
    jobs = TypeAdapter(list[UserJob]).validate_python(rows)

    valid_jobs = []
    invalid_jobs = []

    for job in jobs:
        if job.status != job.info.type:
            invalid_jobs.append(job)
            continue

        valid_jobs.append(job)

    return JobsByUser(
        valid_jobs=valid_jobs,
        invalid_jobs=invalid_jobs,
    )
