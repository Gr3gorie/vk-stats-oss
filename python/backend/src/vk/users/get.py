from datetime import datetime
from enum import Enum
from typing import Annotated, Any

import pydantic
import structlog
from pydantic import BeforeValidator, Field

from ..client import Client
from ..request import VkApiRequest

log = structlog.stdlib.get_logger()

DEFAULT_FIELDS = "bdate, relation, city, country, deactivated, sex, last_seen, personal"


class GetUsersRequest(VkApiRequest):
    user_ids: str
    fields: str = DEFAULT_FIELDS


class Sex(Enum):
    WOMAN = 1
    MAN = 2


def zero_to_none(input: Any) -> Any:
    if input == 0:
        return None
    return input


def parse_date(input: Any) -> datetime | None:
    if not isinstance(input, str):
        return None
    date = input.split(".")
    date = list(map(int, date))

    try:
        match date:
            case [day, month, year]:
                return datetime(year=year, month=month, day=day)
            case [day, month]:
                return datetime(year=1904, month=month, day=day)
            case _:
                return None
    except ValueError as e:
        log.warning("Failed to parse date", input=input, error=e)
        return None


class Relation(Enum):
    SINGLE = 1
    DATING = 2
    ENGAGED = 3
    MARRIED = 4
    COMPLICATED = 5
    ACTIVELY_SEARCHING = 6
    IN_LOVE = 7
    IN_A_CIVIL_UNION = 8


class Political(Enum):
    COMMUNIST = 1
    SOCIALIST = 2
    MODERATE = 3
    LIBERAL = 4
    CONSERVATIVE = 5
    MONARCHIST = 6
    ULTRACONSERVATIVE = 7
    INDIFFERENT = 8
    LIBERTARIAN = 9


class PeopleMain(Enum):
    INTELLIGENCE_AND_CREATIVITY = 1
    KINDNESS_AND_HONESTY = 2
    BEAUTY_AND_HEALTH = 3
    POWER_AND_WEALTH = 4
    COURAGE_AND_PERSISTENCE = 5
    HUMOR_AND_LOVE_FOR_LIFE = 6


class LifeMain(Enum):
    FAMILY_AND_CHILDREN = 1
    CAREER_AND_MONEY = 2
    ENTERTAINMENT_AND_LEISURE = 3
    SCIENCE_AND_RESEARCH = 4
    IMPROVING_THE_WORLD = 5
    SELF_DEVELOPMENT = 6
    BEAUTY_AND_ART = 7
    FAME_AND_INFLUENCE = 8


class Smoking(Enum):
    STRONGLY_NEGATIVE = 1
    NEGATIVE = 2
    COMPROMISABLE = 3
    NEUTRAL = 4
    POSITIVE = 5


class Alcohol(Enum):
    STRONGLY_NEGATIVE = 1
    NEGATIVE = 2
    COMPROMISABLE = 3
    NEUTRAL = 4
    POSITIVE = 5


class Personal(pydantic.BaseModel):
    political: Annotated[Political | None, BeforeValidator(zero_to_none)] = None
    langs: list[str] = Field(..., default_factory=list)
    people_main: Annotated[PeopleMain | None, BeforeValidator(zero_to_none)] = None
    life_main: Annotated[LifeMain | None, BeforeValidator(zero_to_none)] = None
    smoking: Annotated[Smoking | None, BeforeValidator(zero_to_none)] = None
    alcohol: Annotated[Alcohol | None, BeforeValidator(zero_to_none)] = None


class City(pydantic.BaseModel):
    id: int
    title: str


class Country(pydantic.BaseModel):
    id: int
    title: str


class LastSeen(pydantic.BaseModel):
    platform: int | None = None
    time: datetime


class User(pydantic.BaseModel):
    id: int

    # Returned if any `fields` were specified in the request.
    first_name: str
    last_name: str
    can_access_closed: bool

    # Additional fields.
    deactivated: str | None = None
    sex: Annotated[Sex | None, BeforeValidator(zero_to_none)] = None
    bdate: Annotated[datetime | None, BeforeValidator(parse_date)] = None
    country: Country | None = None
    city: City | None = None
    last_seen: LastSeen | None = None
    relation: Annotated[Relation | None, BeforeValidator(zero_to_none)] = None
    personal: Personal | None = None


class GetUsersResponse(pydantic.BaseModel):
    users: list[User]


class _GetUsersResponseOuter(pydantic.BaseModel):
    response: list[User]


async def get_users(
    client: Client,
    request: GetUsersRequest,
) -> GetUsersResponse:
    response = await client._get(
        url="https://api.vk.com/method/users.get",
        params=request.model_dump(),
        response_model=_GetUsersResponseOuter,
    )

    return GetUsersResponse(users=response.response)
