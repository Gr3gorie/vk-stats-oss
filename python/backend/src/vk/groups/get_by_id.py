import structlog
from pydantic import BaseModel

from ..client import Client
from ..request import VkApiRequest

log = structlog.stdlib.get_logger()


class GetByIdRequest(VkApiRequest):
    # Ids or screen names. Max 500.
    group_ids: str
    fields: str = "members_count"


class GroupById(BaseModel):
    id: int
    name: str
    screen_name: str
    members_count: int
    photo_50: str | None = None
    photo_100: str | None = None
    photo_200: str | None = None


class GetByIdResponse(BaseModel):
    groups: list[GroupById]


class _GetByIdResponseOuter(BaseModel):
    response: GetByIdResponse


async def get_by_id(
    client: Client,
    request: GetByIdRequest,
) -> GetByIdResponse:
    response = await client._get(
        url="https://api.vk.com/method/groups.getById",
        params=request.model_dump(),
        response_model=_GetByIdResponseOuter,
    )

    return response.response
