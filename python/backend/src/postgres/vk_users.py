from datetime import datetime

import asyncpg
import vk


async def upsert(
    conn: asyncpg.Connection,
    user: vk.users.User,
    last_updated_at: datetime,
) -> None:
    if user.personal and user.personal.political:
        political = user.personal.political.value
    else:
        political = None

    if user.personal and user.personal.people_main:
        people_main = user.personal.people_main.value
    else:
        people_main = None

    if user.personal and user.personal.life_main:
        life_main = user.personal.life_main.value
    else:
        life_main = None

    if user.personal and user.personal.smoking:
        smoking = user.personal.smoking.value
    else:
        smoking = None

    if user.personal and user.personal.alcohol:
        alcohol = user.personal.alcohol.value
    else:
        alcohol = None

    await conn.execute(
        """
            INSERT INTO vk_users(
                  id
                , first_name
                , last_name
                , can_access_closed
                , deactivated
                , last_seen
                , sex
                , bdate
                , country
                , city
                , relation
                , political
                , langs
                , people_main
                , life_main
                , smoking
                , alcohol
                , last_updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            ON CONFLICT (id) DO UPDATE
            SET first_name = EXCLUDED.first_name
              , last_name = EXCLUDED.last_name
              , can_access_closed = EXCLUDED.can_access_closed
              , deactivated = EXCLUDED.deactivated
              , last_seen = EXCLUDED.last_seen
              , sex = EXCLUDED.sex
              , bdate = EXCLUDED.bdate
              , country = EXCLUDED.country
              , city = EXCLUDED.city
              , relation = EXCLUDED.relation
              , political = EXCLUDED.political
              , langs = EXCLUDED.langs
              , people_main = EXCLUDED.people_main
              , life_main = EXCLUDED.life_main
              , smoking = EXCLUDED.smoking
              , alcohol = EXCLUDED.alcohol
              , last_updated_at = EXCLUDED.last_updated_at
        """,
        user.id,
        user.first_name,
        user.last_name,
        user.can_access_closed,
        user.deactivated,
        user.last_seen.time if user.last_seen else None,
        user.sex.value if user.sex else None,
        user.bdate,
        user.country.title if user.country else None,
        user.city.title if user.city else None,
        user.relation.value if user.relation else None,
        political,
        user.personal.langs if user.personal else None,
        people_main,
        life_main,
        smoking,
        alcohol,
        last_updated_at,
    )
