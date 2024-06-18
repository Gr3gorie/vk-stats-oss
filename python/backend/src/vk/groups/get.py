import pydantic

from ..client import Client
from ..pagination import VK_PAGINATION_MAX_ITEMS
from ..request import VkApiRequest


class GetGroupsRequest(VkApiRequest):
    user_id: int
    count: int = VK_PAGINATION_MAX_ITEMS
    offset: int = 0


class GetGroupsResponse(pydantic.BaseModel):
    items: list[int]
    count: int


class _GetGroupsResponseOuter(pydantic.BaseModel):
    response: GetGroupsResponse


async def get_groups(
    client: Client,
    request: GetGroupsRequest,
) -> GetGroupsResponse:
    response = await client._get(
        url="https://api.vk.com/method/groups.get",
        params=request.model_dump(),
        response_model=_GetGroupsResponseOuter,
    )
    return response.response
