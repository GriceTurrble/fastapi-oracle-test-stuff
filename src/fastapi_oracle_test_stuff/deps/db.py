"""Database engine and sessionmaker dependency for FastAPI routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fastapi_oracle_test_stuff.deps.settings import Settings, SettingsDep

type AsyncSessionMakerType = async_sessionmaker[AsyncSession]

_async_session_maker_cache: dict[str, AsyncSessionMakerType] = {}


def _build_async_session_maker(settings: Settings) -> AsyncSessionMakerType:
    if "default" not in _async_session_maker_cache:
        db_settings = settings.db
        url = URL.create(
            drivername="oracle+oracledb",
            username=db_settings.user,
            password=db_settings.password.get_secret_value(),
            host=db_settings.host,
            port=db_settings.port,
            query={"service_name": db_settings.service},
        )
        async_engine = create_async_engine(url)
        _async_session_maker_cache["default"] = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
        )

    return _async_session_maker_cache["default"]


def get_async_session_maker(settings: SettingsDep) -> AsyncSessionMakerType:
    return _build_async_session_maker(settings=settings)


AsyncSessionMakerDep = Annotated[
    AsyncSessionMakerType,
    Depends(get_async_session_maker),
]
"""Inject to get the shared `async_sessionmaker`, then open a session where
the transaction boundary actually belongs (typically in the route or service
function), e.g.:

    async def list_authors(async_sessionmaker: AsyncSessionMakerDep):
        async with async_sessionmaker() as session:
            ...

This dependency intentionally yields the sessionmaker itself rather than an
already-open `AsyncSession`, so callers control when a session/transaction
starts and ends instead of one being opened for every request regardless of
whether it's needed.
"""
