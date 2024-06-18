from httpx import QueryParams
from pydantic import BaseModel


class BuildAuthorizeUrlOptions(BaseModel):
    client_id: int
    redirect_uri: str

    scope: int = (
        # Offline.
        (1 << 16)
        # Stats.
        | (1 << 20)
    )
    state: str = "vk-stats-auth-state"

    # It's probably a bad idea to change these.
    display: str = "page"
    response_type: str = "code"


def build_authorize_url(options: BuildAuthorizeUrlOptions) -> str:
    query_params = QueryParams(options.model_dump())
    return f"https://oauth.vk.com/authorize?{str(query_params)}"
