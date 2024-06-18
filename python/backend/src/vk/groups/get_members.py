import pydantic
from pydantic import AliasChoices, Field

from ..client import Client
from ..request import VkApiRequest


class GetMembersRequest(VkApiRequest):
    # Either id or screen name.
    # Speculation: screen name cannot start with a digit.
    # Example: "https://vk.com/durov" -> "durov"
    group_id: int | str

    count: int
    offset: int = 0
    # TODO: Consider adding `fields` like in `GetUsersRequest`.
    # fields: str | None = None


class GetMembersResponse(pydantic.BaseModel):
    count: int
    member_ids: list[int] = Field(validation_alias=AliasChoices("items"))


class _GetMembersResponseOuter(pydantic.BaseModel):
    response: GetMembersResponse


async def get_members(
    client: Client,
    request: GetMembersRequest,
) -> GetMembersResponse:
    response = await client._get(
        url="https://api.vk.com/method/groups.getMembers",
        params=request.model_dump(),
        response_model=_GetMembersResponseOuter,
    )

    return response.response
