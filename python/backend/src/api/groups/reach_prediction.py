from datetime import datetime, timedelta
import math
from typing import Literal

import pandas
import postgres
import structlog
import vk
from fastapi import HTTPException
from prophet import Prophet
from pydantic import BaseModel, TypeAdapter
from vk.errors import TransientError, with_transient_error_retry
from vk.groups.get_by_id import GetByIdRequest
from vk.stats.get import GetStatsRequest
from vk_extra.group_url import VkGroupUrl

from api.auth.cookie import AuthCookieValueExtractor
from api.state import ApiStateExtractor

log = structlog.stdlib.get_logger()


class GroupsPredictReach:
    class Request(BaseModel):
        group_url: VkGroupUrl
        period_from: datetime
        granularity: Literal["DAY", "WEEK", "MONTH"]

    class Response(BaseModel):
        class Reach(BaseModel):
            date: str  # "dd.mm.yyyy"
            reach: int

            @staticmethod
            def from_lists(
                dates: list[datetime], reach: list[float]
            ) -> "list[GroupsPredictReach.Response.Reach]":
                return list(
                    map(
                        lambda pair: GroupsPredictReach.Response.Reach(
                            date=pair[0].strftime("%d.%m.%Y"),
                            reach=int(0 if math.isnan(pair[1]) else int(pair[1])),
                        ),
                        zip(dates, reach),
                    )
                )

        group_name: str
        existing: list[Reach]
        # From today and 7 days forwards (for now).
        prediction: list[Reach]


async def predict_reach(
    state: ApiStateExtractor,
    auth: AuthCookieValueExtractor,
    request: GroupsPredictReach.Request,
) -> GroupsPredictReach.Response:
    user_access_token = await postgres.vk_oauth_tokens.select_access_token(
        state.pg_pool,
        user_id=auth.user_id,
    )
    if not user_access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_vk_client = state.vk_client.with_new_access_token(user_access_token)

    async def get_group_by_screen_name(_error: TransientError | None):
        return await vk.groups.get_by_id(
            user_vk_client,
            GetByIdRequest(group_ids=request.group_url.screen_name),
        )

    response = await with_transient_error_retry(get_group_by_screen_name)
    if not response.groups:
        raise HTTPException(status_code=404, detail="Group not found")
    group = response.groups[0]

    # NB: VK randomly doesn't return data of each consecutive 100 days for each 200 days,
    # so we make two requests one of which is shifted by 100 days and then we merge them.
    first_half_response = await vk.stats.get_stats(
        client=user_vk_client,
        request=GetStatsRequest(
            group_id=group.id,
            timestamp_from=int(request.period_from.timestamp()),
            timestamp_to=int(datetime.now().timestamp()),
        ),
    )
    second_half_response = await vk.stats.get_stats(
        client=user_vk_client,
        request=GetStatsRequest(
            group_id=group.id,
            timestamp_from=int((request.period_from - timedelta(days=100)).timestamp()),
            timestamp_to=int((datetime.now() - timedelta(days=100)).timestamp()),
        ),
    )

    # TODO: Extract CPU-bound code to a separate threadpool.
    df = pandas.DataFrame(
        {
            "ds": list(
                map(
                    lambda s: s.period_from.replace(tzinfo=None),
                    first_half_response.stats,
                )
            )
            + list(
                map(
                    lambda s: s.period_from.replace(tzinfo=None),
                    second_half_response.stats,
                )
            ),
            "y": list(map(lambda s: s.reach.reach, first_half_response.stats))
            + list(map(lambda s: s.reach.reach, second_half_response.stats)),
        }
    )

    df = df.sort_values(by="ds")
    df = df[df["y"] > 0]

    # Drop the last row (which is the reach for today).
    df = df.iloc[:-1]

    match request.granularity:
        case "DAY":
            df_existing = df.reset_index(drop=True)
        case "WEEK":
            df_existing = df.set_index("ds").resample("W").mean().reset_index()
        case "MONTH":
            df_existing = df.set_index("ds").resample("M").mean().reset_index()

    model = Prophet(
        seasonality_mode="multiplicative",
        yearly_seasonality=True,  # type: ignore
        weekly_seasonality=True,  # type: ignore
        daily_seasonality=False,  # type: ignore
        seasonality_prior_scale=10.0,
        changepoint_prior_scale=0.1,
    )

    model.fit(df_existing)

    match request.granularity:
        case "DAY":
            periods = 10
            freq = "D"
        case "WEEK":
            periods = 6
            freq = "W"
        case "MONTH":
            periods = 3
            freq = "M"

    df_future = model.make_future_dataframe(
        periods=periods, freq=freq, include_history=False
    )
    output = model.predict(df_future)

    prediction_dates, prediction_reach = _extract_dates_and_reach(output, target="yhat")
    prediction = GroupsPredictReach.Response.Reach.from_lists(
        dates=prediction_dates,
        reach=prediction_reach,
    )

    existing_df = df_existing[
        df_existing["ds"] >= request.period_from.replace(tzinfo=None)
    ]
    existing_dates, existing_reach = _extract_dates_and_reach(existing_df, target="y")
    existing = GroupsPredictReach.Response.Reach.from_lists(
        dates=existing_dates,
        reach=existing_reach,
    )

    return GroupsPredictReach.Response(
        group_name=group.name,
        existing=existing,
        prediction=prediction,
    )


def _extract_dates_and_reach(
    df: pandas.DataFrame, target: Literal["y", "yhat"]
) -> tuple[list[datetime], list[float]]:
    return TypeAdapter(tuple[list[datetime], list[float]]).validate_python(
        (
            df["ds"],
            df[target],
        )
    )
