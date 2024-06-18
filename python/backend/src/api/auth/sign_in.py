import uuid
from urllib.parse import urlparse

import jwt
import postgres
import structlog
import vk
from fastapi import Response
from pydantic import BaseModel
from utils import utc_now
from vk.oauth.access_token import GetAccessTokenRequest
from vk.oauth.authorize import BuildAuthorizeUrlOptions
from vk.users.get import GetUsersRequest

from api.state import ApiStateExtractor

from .cookie import AUTH_COOKIE_ENCRYPTION_ALGORITHM, AUTH_COOKIE_NAME, AuthCookieValue

log = structlog.stdlib.get_logger()


# --------------------------------------------------------------------------------------------------


class SignInInfo(BaseModel):
    authorize_url: str


def get_sign_in_info(
    api_state: ApiStateExtractor,
    redirect_uri: str,
    state: str | None = None,
) -> SignInInfo:
    options = BuildAuthorizeUrlOptions(
        client_id=api_state.vk_config.client_id,
        redirect_uri=redirect_uri,
    )
    options.state = state or options.state

    authorize_url = vk.oauth.build_authorize_url(options)

    return SignInInfo(
        authorize_url=authorize_url,
    )


# --------------------------------------------------------------------------------------------------


class FinishSignInRequest(BaseModel):
    code: str
    redirect_uri: str


async def finish_sign_in(
    api_state: ApiStateExtractor,
    response: Response,
    request: FinishSignInRequest,
) -> None:
    code = request.code
    redirect_uri = request.redirect_uri
    log.info("Received finish sign in request", code=code, redirect_uri=redirect_uri)

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

    user_vk_client = api_state.vk_client.with_new_access_token(access_token)
    user_response = await vk.users.get_users(
        user_vk_client, GetUsersRequest(user_ids=str(user_id))
    )
    user = user_response.users[0]

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

        await postgres.vk_users.upsert(conn, user, utc_now())

    cookie_value = AuthCookieValue(
        user_id=user_id,
        user_first_name=user.first_name,
        user_last_name=user.last_name,
    )
    encoded_cookie = jwt.encode(
        payload=cookie_value.model_dump(),
        key=api_state.backend_config.auth_private_key,
        algorithm=AUTH_COOKIE_ENCRYPTION_ALGORITHM,
    )

    domain = urlparse(redirect_uri).hostname
    domain = f".{domain}" if domain else ""
    expires = 60 * 60 * 24 * 7
    log.debug(
        "Setting auth cookie",
        domain=domain,
        expires=expires,
    )
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=encoded_cookie,
        domain=domain,
        expires=expires,
        httponly=True,
        samesite="none",
        secure=True,
    )
