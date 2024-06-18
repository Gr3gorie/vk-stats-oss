from pydantic import BaseModel

from api.auth import (
    AuthCookieValueExtractor,
)


class User(BaseModel):
    user_id: int


async def get_me(
    auth: AuthCookieValueExtractor,
) -> User:
    return User(
        user_id=auth.user_id,
    )
