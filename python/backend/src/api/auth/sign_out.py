from fastapi import Response

from .cookie import AUTH_COOKIE_NAME


def sign_out(response: Response) -> None:
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        samesite="none",
        secure=True,
    )
