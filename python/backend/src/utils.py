import datetime
import os


def get_env_or_raise(name: str, config: dict[str, str] | None = None) -> str:
    if config is None:
        value = os.environ.get(name)
    else:
        value = config.get(name)

    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return value


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)
