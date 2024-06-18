from dataclasses import dataclass

import structlog
from pydantic import BaseModel

from ..client import Client
from ..execute import VK_EXECUTE_MAX_REQUESTS
from ..pagination import VK_PAGINATION_MAX_ITEMS
from ..request import VK_API_VERSION

log = structlog.stdlib.get_logger()


@dataclass
class GetMembersViaExecuteRequest:
    group_id: int
    offset: int
    count: int = VK_EXECUTE_MAX_REQUESTS * VK_PAGINATION_MAX_ITEMS


class GetMembersViaExecuteResponse(BaseModel):
    total_count: int
    member_ids: list[int]


class _GetMembersViaExecuteCallResult(BaseModel):
    count: int
    items: list[int]


class _GetMembersViaExecuteResponse(BaseModel):
    response: list[_GetMembersViaExecuteCallResult]


async def get_members_via_execute(
    client: Client,
    request: GetMembersViaExecuteRequest,
) -> GetMembersViaExecuteResponse:
    calls = []

    for offset in range(
        request.offset, request.offset + request.count, VK_PAGINATION_MAX_ITEMS
    ):
        group_id = request.group_id
        count = VK_PAGINATION_MAX_ITEMS
        call = f"""API.groups.getMembers({{"group_id":{group_id},"count":{count},"offset":{offset}}})"""
        calls.append(call)

    joined_calls = ",".join(calls)
    code = f"""return[{joined_calls}];"""

    response = await client._get(
        url="https://api.vk.com/method/execute",
        params={"code": code, "v": VK_API_VERSION},
        response_model=_GetMembersViaExecuteResponse,
    )

    total_count = response.response[0].count

    return GetMembersViaExecuteResponse(
        total_count=total_count,
        member_ids=[
            member_id
            for call_result in response.response
            for member_id in call_result.items
        ],
    )
