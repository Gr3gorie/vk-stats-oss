import pydantic

VK_API_VERSION = "5.236"


class VkApiRequest(pydantic.BaseModel):
    v: str = VK_API_VERSION
