import pydantic

from ..client import Client
from ..request import VkApiRequest


class GetSubscriptionsRequest(VkApiRequest):
    user_id: int


class Subscriptions(pydantic.BaseModel):
    items: list[int]
    count: int


class GetSubscriptionsResponse(pydantic.BaseModel):
    users: Subscriptions
    groups: Subscriptions


class _GetSubscriptionsResponseOuter(pydantic.BaseModel):
    response: GetSubscriptionsResponse


async def get_subscriptions(
    client: Client,
    request: GetSubscriptionsRequest,
) -> GetSubscriptionsResponse:
    response = await client._get(
        url="https://api.vk.com/method/users.getSubscriptions",
        params=request.model_dump(),
        response_model=_GetSubscriptionsResponseOuter,
    )
    return response.response
