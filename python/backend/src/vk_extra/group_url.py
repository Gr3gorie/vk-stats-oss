from typing import Annotated, Union

from pydantic import AfterValidator, Field, RootModel, TypeAdapter
from pydantic.networks import AnyHttpUrl

#  --------------------------------------------------------------------------------------------------


class VkGroupUrlErrors:
    class NotVkHost(ValueError):
        pass

    class MissingGroupInPathname(ValueError):
        pass


VkGroupUrlError = Annotated[
    Union[
        VkGroupUrlErrors.NotVkHost,
        VkGroupUrlErrors.MissingGroupInPathname,
    ],
    # ...,
    Field(..., discriminator="kind"),
]

#  --------------------------------------------------------------------------------------------------


def _ensure_vk_host(url: AnyHttpUrl) -> AnyHttpUrl:
    if url.host != "vk.com":
        raise VkGroupUrlErrors.NotVkHost("Only https://vk.com URLs are supported")

    return url


def _ensure_has_group_in_path(url: AnyHttpUrl) -> AnyHttpUrl:
    parts = (url.path or "").strip("/").split("/")
    if not parts or not parts[0].strip():
        raise VkGroupUrlErrors.MissingGroupInPathname("URL is missing path")

    return url


#  --------------------------------------------------------------------------------------------------


class VkGroupUrl(RootModel):
    root: Annotated[
        AnyHttpUrl,
        AfterValidator(_ensure_vk_host),
        AfterValidator(_ensure_has_group_in_path),
    ]

    @staticmethod
    def parse(url: str) -> "VkGroupUrl":
        return TypeAdapter(VkGroupUrl).validate_python(url)

    @property
    def screen_name(self) -> str:
        parts = (self.root.path or "").strip("/").split("/")
        return parts[0]
