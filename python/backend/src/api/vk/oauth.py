import uuid

import jwt
import structlog
import vk
from fastapi import Response
from vk.oauth.access_token import GetAccessTokenRequest

from api.auth import (
    AUTH_COOKIE_ENCRYPTION_ALGORITHM,
    AUTH_COOKIE_NAME,
    AuthCookieValue,
)
from api.state import ApiStateExtractor

log = structlog.stdlib.get_logger()


async def handle_oauth_callback(
    api_state: ApiStateExtractor,
    response: Response,
    code: str,
    redirect_uri: str | None = None,
    state: str | None = None,
):
    redirect_uri = redirect_uri or api_state.backend_config.vk_redirect_uri
    log.info(
        "Received OAuth callback", code=code, state=state, redirect_uri=redirect_uri
    )

    access_token_request = GetAccessTokenRequest(
        client_id=api_state.vk_config.client_id,
        client_secret=api_state.vk_config.client_secret,
        redirect_uri=redirect_uri,
        code=code,
    )
    access_token_response = await vk.oauth.get_access_token(
        api_state.vk_client,
        access_token_request,
    )
    user_id = access_token_response.user_id
    access_token = access_token_response.access_token

    auth_session_id = uuid.uuid4()

    async with api_state.pg_pool.acquire() as conn:
        await conn.execute(
            """
                INSERT INTO vk_oauth_tokens(
                    id, user_id, access_token
                )
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET access_token = EXCLUDED.access_token
            """,
            uuid.uuid4(),
            user_id,
            access_token,
        )

        await conn.execute(
            """
                INSERT INTO auth_sessions(id, user_id)
                VALUES ($1, $2)
            """,
            auth_session_id,
            user_id,
        )

    cookie_value = AuthCookieValue(user_id=user_id)
    encoded_cookie = jwt.encode(
        payload=cookie_value.model_dump(),
        key=api_state.backend_config.auth_private_key,
        algorithm=AUTH_COOKIE_ENCRYPTION_ALGORITHM,
    )
    response.set_cookie(key=AUTH_COOKIE_NAME, value=encoded_cookie)

    # TODO: Redirect to the frontend.
    return "Hello from vk-stats! Thanks for logging in!"
