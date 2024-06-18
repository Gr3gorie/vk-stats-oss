from fastapi import APIRouter

from .average_portrait import request_average_portrait, view_average_portrait_request
from .get import get_users


def build_router() -> APIRouter:
    r = APIRouter()

    r.add_api_route(
        methods=["POST"],
        path="/average-portrait",
        endpoint=request_average_portrait,
    )
    r.add_api_route(
        methods=["GET"],
        path="/average-portrait/{request_id}",
        endpoint=view_average_portrait_request,
    )

    r.add_api_route(
        methods=["POST"],
        path="/",
        endpoint=get_users,
    )

    return r
