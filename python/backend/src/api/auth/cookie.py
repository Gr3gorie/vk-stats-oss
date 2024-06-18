from typing import Annotated

import jwt
import structlog
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError

from api.state import ApiStateExtractor

log = structlog.stdlib.get_logger()

#  --------------------------------------------------------------------------------------------------

# Use generic cookie name to prevent framework detection.
AUTH_COOKIE_NAME = "sid"

AUTH_COOKIE_ENCRYPTION_ALGORITHM = "RS256"

#  --------------------------------------------------------------------------------------------------


class AuthCookieValue(BaseModel):
    user_id: int
    user_first_name: str
    user_last_name: str


#  --------------------------------------------------------------------------------------------------


def _extract_auth_cookie_value_or_raise(
    state: ApiStateExtractor,
    request: Request,
) -> AuthCookieValue:
    cookie = request.cookies.get(AUTH_COOKIE_NAME)
    if not cookie:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        decoded = jwt.decode(
            jwt=cookie,
            key=state.backend_config.auth_public_key,
            algorithms=[AUTH_COOKIE_ENCRYPTION_ALGORITHM],
        )
    except jwt.InvalidSignatureError as e:
        log.debug("Invalid signature in auth cookie", error=e)
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            # Clear the cookie.
            headers={"set-cookie": f"{AUTH_COOKIE_NAME}=; Path=/; Max-Age=0"},
        )

    try:
        return AuthCookieValue.model_validate(decoded)
    except ValidationError as e:
        log.warn("Failed to parse auth cookie", error=e)
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            # Clear the cookie.
            headers={"set-cookie": f"{AUTH_COOKIE_NAME}=; Path=/; Max-Age=0"},
        )


AuthCookieValueExtractor = Annotated[
    AuthCookieValue,
    Depends(_extract_auth_cookie_value_or_raise),
]
