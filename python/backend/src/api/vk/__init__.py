from urllib.parse import urlparse

from config import BackendConfig
from fastapi import APIRouter

from .oauth import handle_oauth_callback


def build_router(backend_config: BackendConfig) -> APIRouter:
    r = APIRouter()

    r.add_api_route(
        methods=["GET"],
        path=urlparse(backend_config.vk_redirect_uri).path,
        endpoint=handle_oauth_callback,
    )

    return r
