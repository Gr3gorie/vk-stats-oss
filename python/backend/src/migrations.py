import asyncpg


async def migrate_postgres(pg_pool: asyncpg.Pool):
    async with pg_pool.acquire() as conn:
        # ------------------------------------------------------------------------------------------
        # Tools.

        await conn.execute(
            """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE 'plpgsql';
            """
        )

        # ------------------------------------------------------------------------------------------
        # Common types.

        await conn.execute(
            """
                DO $$ BEGIN
                    CREATE TYPE job_status AS ENUM (
                          'PENDING'
                        , 'RUNNING'
                        , 'CANCELLED'
                        , 'SUCCEEDED'
                        , 'FAILED'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """
        )

        # ------------------------------------------------------------------------------------------
        # Group update jobs.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS group_update_jobs (
                      id UUID PRIMARY KEY DEFAULT gen_random_uuid()

                    , request_id UUID NOT NULL
                    , user_id    INT  NOT NULL

                    , group_id INT        NOT NULL
                    , status   job_status NOT NULL
                    , info     JSONB      NOT NULL

                    , created_at TIMESTAMPTZ DEFAULT NOW()
                    , updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """
        )
        await conn.execute(
            """
                DO $$ BEGIN
                    CREATE TRIGGER update_group_update_jobs_updated_at
                    BEFORE UPDATE ON group_update_jobs
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """
        )

        # ------------------------------------------------------------------------------------------
        # Group member intersection requests.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS group_member_intersection_requests(
                      id UUID PRIMARY KEY DEFAULT gen_random_uuid()

                    , user_id INT NOT NULL

                    -- TODO: Maybe it makes sense to add check for LENGTH >= 1.
                    , group_ids      INT[]  NOT NULL
                    , update_job_ids UUID[] NOT NULL

                    , created_at TIMESTAMPTZ DEFAULT NOW()
                    , updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """
        )
        await conn.execute(
            """
                DO $$ BEGIN
                    CREATE TRIGGER update_group_member_intersection_requests_updated_at
                    BEFORE UPDATE ON group_member_intersection_requests
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """
        )

        # ------------------------------------------------------------------------------------------
        # User average portrait requests.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS user_average_portrait_requests (
                      id UUID PRIMARY KEY DEFAULT gen_random_uuid()

                    , user_id INT NOT NULL

                    , group_ids      INT[]  NOT NULL
                    , update_job_ids UUID[] NOT NULL

                    , created_at TIMESTAMPTZ DEFAULT NOW()
                    , updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """
        )
        await conn.execute(
            """
                DO $$ BEGIN
                    CREATE TRIGGER update_user_average_portrait_requests_updated_at
                    BEFORE UPDATE ON user_average_portrait_requests
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """
        )

        # ------------------------------------------------------------------------------------------
        # VK users.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS vk_users (
                      id INT PRIMARY KEY

                    , first_name VARCHAR(30) NOT NULL
                    , last_name  VARCHAR(30) NOT NULL

                    , can_access_closed BOOLEAN NOT NULL
                    , deactivated       VARCHAR(15)
                    , last_seen         TIMESTAMPTZ

                    , sex     SMALLINT NOT NULL
                    , bdate   DATE
                    , country VARCHAR(30)
                    , city    VARCHAR(30)

                    , relation    SMALLINT
                    , political   SMALLINT
                    , langs       TEXT[] DEFAULT '{}'
                    , people_main SMALLINT
                    , life_main   SMALLINT
                    , smoking     SMALLINT
                    , alcohol     SMALLINT

                    -- Our data.
                    , last_updated_at TIMESTAMPTZ
                );
            """
        )

        # ------------------------------------------------------------------------------------------
        # VK groups.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS vk_groups (
                      id INT PRIMARY KEY

                    , name          VARCHAR(128) NOT NULL
                    , screen_name   VARCHAR(128) NOT NULL
                    , members_count INT          NOT NULL

                    , photo_50  VARCHAR(1024)
                    , photo_100 VARCHAR(1024)
                    , photo_200 VARCHAR(1024)

                    -- Our data.
                    , last_updated_at TIMESTAMPTZ
                );
            """
        )

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS vk_group_members (
                      group_id INT NOT NULL
                    , user_id  INT NOT NULL

                    , UNIQUE(group_id, user_id)
                );
            """
        )

        # ------------------------------------------------------------------------------------------
        # Auth.

        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS vk_oauth_tokens (
                      id UUID PRIMARY KEY DEFAULT gen_random_uuid()

                    , user_id      INT          NOT NULL
                    , access_token VARCHAR(256) NOT NULL

                    , created_at TIMESTAMPTZ DEFAULT NOW()

                    -- Don't forget to add `ON CONFLICT (user_id)`.
                    , UNIQUE(user_id)
                )
            """
        )
        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS auth_sessions (
                      id UUID primary key DEFAULT gen_random_uuid()

                    , user_id INT NOT NULL

                    , created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """
        )
