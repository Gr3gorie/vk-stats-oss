from fastapi import APIRouter

from .last_updated import get_last_updated
from .member_intersection import (
    request_member_intersection,
    view_member_intersection_request,
)
from .reach_prediction import predict_reach


def build_router() -> APIRouter:
    r = APIRouter()

    r.add_api_route(
        methods=["POST"],
        path="/member-intersection",
        endpoint=request_member_intersection,
    )
    r.add_api_route(
        methods=["GET"],
        path="/member-intersection/{request_id}",
        endpoint=view_member_intersection_request,
    )

    r.add_api_route(
        methods=["GET"],
        path="/last-updated",
        endpoint=get_last_updated,
    )

    r.add_api_route(
        methods=["POST"],
        path="/reach/predict",
        endpoint=predict_reach,
    )

    return r
