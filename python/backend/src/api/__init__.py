from config import BackendConfig
from fastapi import APIRouter

from . import auth, groups, users, vk
from .dependencies import get_dependency, inject_dependency
from .state import ApiState


def build_router(backend_config: BackendConfig) -> APIRouter:
    r = APIRouter()

    r.include_router(
        prefix="/auth",
        router=auth.build_router(),
    )

    r.include_router(
        prefix="/groups",
        router=groups.build_router(),
    )
    r.include_router(
        prefix="/users",
        router=users.build_router(),
    )

    r.include_router(
        router=vk.build_router(backend_config),
    )

    return r


__all__ = [
    "ApiState",
    "build_router",
    "inject_dependency",
    "get_dependency",
    "auth",
]
