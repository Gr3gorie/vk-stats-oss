import json
from typing import NoReturn, TypeVar

import httpx
import pendulum
import structlog
from httpx._types import HeaderTypes, QueryParamTypes, RequestData
from pydantic import BaseModel, ValidationError

from .errors import (
    VK_ACCESS_DENIED_CODE,
    VK_RATE_LIMIT_CODE,
    AccessDeniedError,
    RateLimitError,
    RequestValidationError,
)

log = structlog.stdlib.get_logger()

Model = TypeVar("Model", bound=BaseModel)


class Client:
    def __init__(self, http_client: httpx.AsyncClient, access_token: str) -> None:
        self.http_client = http_client
        self.access_token = access_token

    def with_new_access_token(self, access_token: str) -> "Client":
        return Client(http_client=self.http_client, access_token=access_token)

    def build_default_headers(self) -> HeaderTypes:
        return {"Authorization": f"Bearer {self.access_token}"}

    async def _get(
        self,
        url: str,
        params: QueryParamTypes,
        response_model: type[Model],
        pass_auth: bool = True,
    ) -> Model:
        raw_response = await self.http_client.get(
            url=url,
            params=params,
            headers=self.build_default_headers() if pass_auth else {},
        )

        try:
            return response_model.model_validate_json(
                json_data=raw_response.text,
                # NB: Using `strict=True` prevents Pydantic from coercing types.
                # Example: `int` (UNIX timestamp) -> `datetime`.
                strict=False,
            )

        except ValidationError as error:
            _try_handle_validation_error(raw_response, error)

    # TODO: Extract common code to `_request` and merge with `_get`.
    async def _post(
        self,
        url: str,
        data: RequestData,
        response_model: type[Model],
        pass_auth: bool = True,
        timeout: float = 30.0,
    ) -> Model:
        raw_response = await self.http_client.post(
            url=url,
            data=data,
            headers=self.build_default_headers() if pass_auth else {},
            timeout=timeout,
        )

        try:
            return response_model.model_validate_json(
                json_data=raw_response.text,
                # NB: Using `strict=True` prevents Pydantic from coercing types.
                # Example: `int` (UNIX timestamp) -> `datetime`.
                strict=False,
            )

        except ValidationError as error:
            _try_handle_validation_error(raw_response, error)


def _try_handle_validation_error(
    response: httpx.Response,
    validation_error: ValidationError,
) -> NoReturn:
    as_json = json.loads(response.text)

    error = as_json.get("error", None)
    if isinstance(error, dict):
        error_code = error.get("error_code", None)
    else:
        error_code = None

    log.debug(
        "Handling validation error", as_json=as_json, error=error, error_code=error_code
    )

    if error_code == VK_RATE_LIMIT_CODE:
        # TODO: Implement and pass different backoff strategies to handle rate limits.
        now = pendulum.now()
        next_second = now.set(microsecond=0).add(seconds=1)

        rate_limit_error = RateLimitError(
            message="Rate limit error",
            response=response,
            # NB:
            #   VK API doesn't provide the exact "retry after" value,
            #   but all of their rate limits are per second.
            retry_after_n_seconds=(next_second - now).total_seconds(),
            # NB: The above doesn't work :(
            # retry_after_n_seconds=0.1,
        )
        raise rate_limit_error from validation_error

    if error_code == VK_ACCESS_DENIED_CODE:
        access_denied_error = AccessDeniedError(
            message="Access to the groups list is denied due to the user's privacy settings",
            response=response,
        )
        raise access_denied_error from validation_error

    request_validation_error = RequestValidationError(
        message="Request validation error",
        response=response,
    )
    raise request_validation_error from validation_error
