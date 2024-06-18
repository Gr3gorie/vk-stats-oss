from pydantic import BaseModel

from ..client import Client


class GetAccessTokenRequest(BaseModel):
    client_id: int
    client_secret: str
    redirect_uri: str
    code: str


class GetAccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    user_id: int


async def get_access_token(
    client: Client,
    request: GetAccessTokenRequest,
) -> GetAccessTokenResponse:
    return await client._get(
        url="https://oauth.vk.com/access_token",
        params=request.model_dump(),
        response_model=GetAccessTokenResponse,
        pass_auth=False,
    )
