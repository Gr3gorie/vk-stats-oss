import vk
from vk.groups import GetGroupsRequest


async def find_groups(
    user_id: int,
) -> list[int]:
    groups = await vk.groups.get_groups(
        GetGroupsRequest(
            user_id=user_id,
            count=1000,
        )
    )
    return groups.items
