from dataclasses import dataclass

import structlog
from pydantic import BaseModel

from vk.client import Client
from vk.request import VK_API_VERSION

from .get import DEFAULT_FIELDS, User

log = structlog.stdlib.get_logger()


@dataclass
class GetUsersViaExecuteRequest:
    user_ids: list[int]  # -> str
    fields: str = DEFAULT_FIELDS


class GetUsersViaExecuteResponse(BaseModel):
    users: list[User]


class _GetUsersViaExecuteResponse(BaseModel):
    response: list[list[User]]


async def get_users_via_execute(
    client: Client,
    request: GetUsersViaExecuteRequest,
) -> GetUsersViaExecuteResponse:
    calls = []

    MAX_USERS_PER_REQUEST = 1000
    for user_id_batch in range(0, len(request.user_ids), MAX_USERS_PER_REQUEST):
        user_ids = request.user_ids[
            user_id_batch : user_id_batch + MAX_USERS_PER_REQUEST
        ]
        user_ids_str = ",".join(str(user_id) for user_id in user_ids)
        call = f"""API.users.get({{"user_ids":"{user_ids_str}","fields":"{request.fields}"}})"""
        calls.append(call)

    joined_calls = ",".join(calls)
    code = f"""return[{joined_calls}];"""

    response = await client._post(
        url="https://api.vk.com/method/execute",
        data={"code": code, "v": VK_API_VERSION},
        response_model=_GetUsersViaExecuteResponse,
        timeout=60.0,
    )

    return GetUsersViaExecuteResponse(
        users=[user for call_result in response.response for user in call_result]
    )
