from . import groups, oauth, stats, users
from .client import Client
from .execute import VK_EXECUTE_MAX_REQUESTS
from .pagination import VK_PAGINATION_MAX_ITEMS

__all__ = [
    "groups",
    "users",
    "VK_PAGINATION_MAX_ITEMS",
    "Client",
    "oauth",
    "stats",
    "VK_EXECUTE_MAX_REQUESTS",
]
