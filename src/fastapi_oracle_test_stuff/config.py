from __future__ import annotations

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseModel):
    user: str
    password: SecretStr
    host: str
    port: int = 1521
    service: str


class Settings(BaseSettings):
    db: DBSettings

    model_config = SettingsConfigDict(
        env_prefix="TESTTHING__",
        env_nested_delimiter="__",
        validate_by_alias=True,
        validate_by_name=True,
    )
