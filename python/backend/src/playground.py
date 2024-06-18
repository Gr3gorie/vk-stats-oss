import asyncio
import httpx
from uuid import UUID
import os
import structlog


import vk
from groups.update_job import GroupUpdateJob, group_update_job

log = structlog.stdlib.get_logger()

# CAT_MEMES_GROUP_ID = 95648824
# INSIDE_THE_TARDIS_GROUP_ID = 39428534
DOCTOR_WHO_GROUP_ID = 7892656


async def main():
    log.info("Starting the VK group update job")

    vk_client = vk.Client(
        http_client=httpx.AsyncClient(),
        api_key=os.environ["VK_API_KEY"],
    )

    await group_update_job(
        vk_client=vk_client,
        pg_pool=None,
        job=GroupUpdateJob(
            id=UUID("f768a081-fae1-4c09-a83f-85d4108847ff"),
            group_id=DOCTOR_WHO_GROUP_ID,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
