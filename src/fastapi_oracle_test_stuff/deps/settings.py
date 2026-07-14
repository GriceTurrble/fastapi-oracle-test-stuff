"""Application settings dependency for FastAPI routes."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
"""Inject to get the cached `Settings` instance, e.g.:

    async def list_authors(settings: SettingsDep):
        ...

`get_settings` is cached, so every request receives the same `Settings`
instance rather than re-reading and re-validating the environment each time.
"""
