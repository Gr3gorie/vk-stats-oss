from dataclasses import dataclass
from typing import Annotated

import asyncpg
import vk
from config import BackendConfig, VkConfig
from fastapi import Depends, Request

from api.dependencies import get_dependency

# --------------------------------------------------------------------------------------------------


@dataclass
class ApiState:
    backend_config: BackendConfig
    vk_config: VkConfig

    pg_pool: asyncpg.Pool
    vk_client: vk.Client


# --------------------------------------------------------------------------------------------------


def _extract_api_state(request: Request) -> ApiState:
    return get_dependency(request.app, ApiState)


ApiStateExtractor = Annotated[
    ApiState,
    Depends(_extract_api_state),
]
