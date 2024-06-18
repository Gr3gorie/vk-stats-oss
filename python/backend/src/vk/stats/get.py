from datetime import datetime
from typing import Literal

import pydantic

from ..client import Client
from ..request import VkApiRequest


class Stats(pydantic.BaseModel):
    class Activity(pydantic.BaseModel):
        comments: int | None = None
        copies: int | None = None
        hidden: int | None = None
        likes: int | None = None
        subscribed: int | None = None
        unsubscribed: int | None = None

    class Visitors(pydantic.BaseModel):
        views: int
        visitors: int

    class Reach(pydantic.BaseModel):
        reach: int
        reach_subscribers: int
        mobile_reach: int

    period_from: datetime
    period_to: datetime
    activity: Activity | None = None
    visitors: Visitors
    reach: Reach


class GetStatsRequest(VkApiRequest):
    group_id: int
    timestamp_from: int
    timestamp_to: int
    extended: Literal[0, 1] = 1


class GetStatsResponse(pydantic.BaseModel):
    stats: list[Stats]


class _GetStatsResponseOuter(pydantic.BaseModel):
    response: list[Stats]


async def get_stats(
    client: Client,
    request: GetStatsRequest,
) -> GetStatsResponse:
    response = await client._get(
        url="https://api.vk.com/method/stats.get",
        params=request.model_dump(),
        response_model=_GetStatsResponseOuter,
    )

    return GetStatsResponse(stats=response.response)
