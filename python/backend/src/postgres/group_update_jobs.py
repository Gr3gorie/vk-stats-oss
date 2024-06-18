from datetime import datetime
from uuid import UUID, uuid4

import asyncpg
from job import JobInfo, JobStatus, PendingJobInfo
from pydantic import BaseModel, TypeAdapter

# --------------------------------------------------------------------------------------------------


async def insert_many(
    pg_pool: asyncpg.Pool,
    *,
    request_id: UUID,
    user_id: int,
    group_ids: list[int],
) -> list[UUID]:
    job_ids = []

    async with pg_pool.acquire() as conn:
        for group_id in group_ids:
            job_id = uuid4()
            job_info = PendingJobInfo(type=JobStatus.Pending)

            await conn.execute(
                """
                    INSERT INTO group_update_jobs (
                        id, request_id, user_id,
                        group_id, status, info
                    )
                    VALUES ($1, $2, $3, $4, $5, $6::JSONB)
                    
                """,
                job_id,
                request_id,
                user_id,
                group_id,
                JobStatus.Pending,
                job_info,
            )

            job_ids.append(job_id)

    return job_ids


# --------------------------------------------------------------------------------------------------


class GroupUpdateJob(BaseModel):
    id: UUID
    group_id: int
    status: JobStatus
    info: JobInfo
    created_at: datetime


async def list_by_ids(
    pg_pool: asyncpg.Pool,
    *,
    job_ids: list[UUID],
) -> list[GroupUpdateJob]:
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
                SELECT *
                FROM group_update_jobs
                WHERE id = ANY($1)
            """,
            job_ids,
        )

    return TypeAdapter(list[GroupUpdateJob]).validate_python(rows)
