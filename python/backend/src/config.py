import os
from dataclasses import dataclass

from utils import get_env_or_raise


@dataclass
class BackendConfig:
    port: int
    num_workers: int
    vk_redirect_uri: str

    auth_private_key: str
    auth_public_key: str

    @staticmethod
    def load_from_env() -> "BackendConfig":
        source = {
            **os.environ,
        }

        port = int(get_env_or_raise("BACKEND_PORT", source))
        num_workers = int(get_env_or_raise("BACKEND_NUM_WORKERS", source))
        vk_redirect_uri = get_env_or_raise("BACKEND_VK_REDIRECT_URI", source)
        auth_private_key = get_env_or_raise("BACKEND_AUTH_PRIVATE_KEY", source).strip()
        auth_public_key = get_env_or_raise("BACKEND_AUTH_PUBLIC_KEY", source).strip()

        return BackendConfig(
            port=port,
            num_workers=num_workers,
            vk_redirect_uri=vk_redirect_uri,
            auth_private_key=auth_private_key,
            auth_public_key=auth_public_key,
        )


@dataclass
class VkConfig:
    client_secret: str
    client_id: int

    service_access_token: str

    @staticmethod
    def load_from_env() -> "VkConfig":
        source = {
            **os.environ,
        }

        client_secret = get_env_or_raise("VK_CLIENT_SECRET", source)
        client_id = int(get_env_or_raise("VK_CLIENT_ID", source))
        service_access_token = get_env_or_raise("VK_SERVICE_ACCESS_TOKEN", source)

        return VkConfig(
            client_secret=client_secret,
            client_id=client_id,
            service_access_token=service_access_token,
        )


@dataclass
class PostgresConfig:
    dsn: str

    @staticmethod
    def load_from_env() -> "PostgresConfig":
        source = {
            **os.environ,
        }

        user = get_env_or_raise("POSTGRES_USER", source)
        password = get_env_or_raise("POSTGRES_PASSWORD", source)
        host = get_env_or_raise("POSTGRES_HOST", source)
        port = get_env_or_raise("POSTGRES_PORT", source)
        db = get_env_or_raise("POSTGRES_DB", source)

        dsn = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        return PostgresConfig(dsn=dsn)
