import pydantic
import vk
from fastapi import HTTPException
from vk.users import GetSubscriptionsRequest


class UsersFindGroupIntersectionRequest(pydantic.BaseModel):
    user_ids: list[int]


class UsersFindGroupIntersectionResponse(pydantic.BaseModel):
    group_ids: list[int]
    num_groups: int

    @staticmethod
    def from_group_ids(
        group_ids: list[int],
    ) -> "UsersFindGroupIntersectionResponse":
        return UsersFindGroupIntersectionResponse(
            group_ids=group_ids,
            num_groups=len(group_ids),
        )


async def find_group_intersection(
    request: UsersFindGroupIntersectionRequest,
) -> UsersFindGroupIntersectionResponse:
    if len(request.user_ids) == 0:
        return UsersFindGroupIntersectionResponse.from_group_ids([])

    if len(request.user_ids) > 5:
        raise HTTPException(status_code=400, detail="Too many users")

    user_group_ids: list[list[int]] = []
    for user_id in request.user_ids:
        subscriptions = await vk.users.get_subscriptions(
            GetSubscriptionsRequest(user_id=user_id)
        )
        user_group_ids.append(subscriptions.groups.items)

    intersection = set(user_group_ids[0])
    for group_ids in user_group_ids[1:]:
        intersection &= set(group_ids)

    return UsersFindGroupIntersectionResponse.from_group_ids(list(intersection))
