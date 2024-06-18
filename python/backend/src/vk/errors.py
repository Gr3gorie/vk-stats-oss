import asyncio
from typing import Awaitable, Callable, TypeVar

import structlog
from httpx import Response

log = structlog.stdlib.get_logger()

# --------------------------------------------------------------------------------------------------

VK_RATE_LIMIT_CODE = 6
VK_ACCESS_DENIED_CODE = 260

# --------------------------------------------------------------------------------------------------


class VkApiError(Exception):
    pass


# --------------------------------------------------------------------------------------------------


class RequestValidationError(VkApiError):
    def __init__(self, message: str, response: Response):
        super().__init__(message)
        self.response = response


# --------------------------------------------------------------------------------------------------


class TransientError(VkApiError):
    pass


# --------------------------------------------------------------------------------------------------

T = TypeVar("T")
Action = Callable[[TransientError | None], Awaitable[T]]


async def with_transient_error_retry(action: Action[T]) -> T:
    attempt = 0
    last_error: TransientError | None = None

    while True:
        try:
            attempt += 1
            return await action(last_error)

        except TransientError as e:
            if isinstance(e, RateLimitError):
                log.debug(
                    "Rate limit error, sleeping before next attempt",
                    retry_after_n_seconds=e.retry_after_n_seconds,
                    attempt=attempt,
                )
                last_error = e
                await asyncio.sleep(e.retry_after_n_seconds)
                continue

            # Handle other transient errors here.

            raise


# --------------------------------------------------------------------------------------------------


class RateLimitError(TransientError):
    def __init__(self, message: str, response: Response, retry_after_n_seconds: float):
        super().__init__(message)
        self.response = response
        self.retry_after_n_seconds = retry_after_n_seconds


# --------------------------------------------------------------------------------------------------


class AccessDeniedError(VkApiError):
    def __init__(self, message: str, response: Response):
        super().__init__(message)
        self.response = response
