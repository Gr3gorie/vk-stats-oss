import asyncio
import json
from typing import Any

import asyncpg
import background
import httpx
import structlog
import uvicorn
import vk
from api import ApiState
from app import build_app
from config import BackendConfig, PostgresConfig, VkConfig
from dotenv import load_dotenv
from migrations import migrate_postgres
from pydantic import BaseModel
from vk.oauth.authorize import BuildAuthorizeUrlOptions

log = structlog.stdlib.get_logger()


async def main():
    load_dotenv(".env.development")

    log.info("Loading configs...")

    backend_config = BackendConfig.load_from_env()
    vk_config = VkConfig.load_from_env()
    pg_config = PostgresConfig.load_from_env()
    log.info("Configs loaded.")

    log.info(
        "VK sign-in URL: %s",
        vk.oauth.build_authorize_url(
            BuildAuthorizeUrlOptions(
                client_id=vk_config.client_id,
                redirect_uri=backend_config.vk_redirect_uri,
            )
        ),
    )

    log.info("Building Postgres pool...")
    pg_pool = await connect_postgres(pg_config)
    log.info("Postgres pool built.")
    log.info("Migrating Postgres...")
    await migrate_postgres(pg_pool)
    log.info("Postgres migrations completed.")

    vk_client = vk.Client(
        http_client=httpx.AsyncClient(),
        access_token=vk_config.service_access_token,
    )

    log.info("Building the app...")
    state = ApiState(
        vk_config=vk_config,
        backend_config=backend_config,
        pg_pool=pg_pool,
        vk_client=vk_client,
    )
    app = build_app(state)
    log.info("App built.")

    uvicorn_config = uvicorn.Config(
        app,
        workers=backend_config.num_workers,
        host="0.0.0.0",
        port=backend_config.port,
        proxy_headers=True,
        log_level="info",
    )
    log.info("Uvicorn config set.")
    uvicorn_server = uvicorn.Server(config=uvicorn_config)
    log.info("Uvicorn server instantiated.")

    log.info("Starting background subsystems...")
    _group_update_driver = asyncio.create_task(
        background.groups.drive_update_jobs(
            pg_pool,
            httpx.AsyncClient(),
            drive_every_n_seconds=5,
        )
    )

    try:
        log.info("Starting Uvicorn server...")
        await uvicorn_server.serve()
        log.info("Uvicorn server stopped gracefully.")
    except Exception as e:
        log.exception("An error occurred while running the Uvicorn server: %s", e)


async def connect_postgres(config: PostgresConfig) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(dsn=config.dsn, init=_init_conn)
    if not pool:
        raise ValueError("Failed to create Postgres connection pool")
    return pool


async def _init_conn(conn: asyncpg.Connection):
    await conn.set_type_codec(
        "JSONB",
        encoder=_jsonb_encoder,
        decoder=_jsonb_decoder,
        schema="pg_catalog",
    )


def _jsonb_encoder(
    # NB: Should be `Unknown`, but there is none.
    value: Any,
) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    raise TypeError("Encoding JSONB type for Postgres without using Pydantic model")


def _jsonb_decoder(
    # NB: Should be `Unknown`, but there is none.
    value: Any,
) -> Any:
    return json.loads(value)


if __name__ == "__main__":
    asyncio.run(main())
