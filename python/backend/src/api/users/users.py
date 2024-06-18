import asyncio

import vk
from vk import VK_PAGINATION_MAX_ITEMS
from vk.errors import RateLimitError
from vk.users import GetUsersRequest, User


async def get_users(user_ids: list[str], backoff_delay: float = 0.34) -> list[User]:
    all_users: list[User] = []

    offset_size = VK_PAGINATION_MAX_ITEMS

    for offset in range(0, len(user_ids), offset_size):
        user_ids_chunk = user_ids[offset : offset + offset_size]

        while True:
            try:
                print("Fetching members with offset", offset)
                response = await vk.users.get_users(
                    GetUsersRequest(user_ids=",".join(user_ids_chunk))
                )
                all_users.extend(response.users)
                break

            except RateLimitError as error:
                print("Received rate limit error, sleeping", error)
                await asyncio.sleep(delay=backoff_delay)

    return all_users
