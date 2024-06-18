from fastapi import APIRouter

from .cookie import (
    AUTH_COOKIE_ENCRYPTION_ALGORITHM,
    AUTH_COOKIE_NAME,
    AuthCookieValue,
    AuthCookieValueExtractor,
)
from .me import get_me
from .sign_in import finish_sign_in, get_sign_in_info
from .sign_out import sign_out


def build_router() -> APIRouter:
    r = APIRouter()

    r.add_api_route(
        methods=["GET"],
        path="/me",
        endpoint=get_me,
    )
    r.add_api_route(
        methods=["GET"],
        path="/sign-in/info",
        endpoint=get_sign_in_info,
    )
    r.add_api_route(
        methods=["POST"],
        path="/sign-in/finish",
        endpoint=finish_sign_in,
    )
    r.add_api_route(
        methods=["POST"],
        path="/sign-out",
        endpoint=sign_out,
    )

    return r


__all__ = [
    "AUTH_COOKIE_ENCRYPTION_ALGORITHM",
    "AuthCookieValue",
    "AUTH_COOKIE_NAME",
    "build_router",
    "AuthCookieValueExtractor",
]
