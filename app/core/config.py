from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    app_name: str = "balancer"
    app_version: str = "0.1.0"
    app_description: str = "A simple financial management system for small businesses."

    default_timezone: str = "Asia/Damascus"

    db_url: str = ""

    debug: bool = True
    echo_sql: bool = True

    jwt_secret_key: str = ""
    jwt_algorithm: str = ""
    jwt_access_token_expires_in_minutes: int = 15
    jwt_refresh_token_expires_in_days: int = 7
    jwt_token_type: str = ""

    default_page_size: int = 10
    default_max_page_size: int = 100

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config() -> Config:
    return Config()
