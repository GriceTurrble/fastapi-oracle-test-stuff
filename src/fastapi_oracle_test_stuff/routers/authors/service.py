from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from fastapi_oracle_test_stuff.deps.db import SessionMakerDep, SessionMakerType
from fastapi_oracle_test_stuff.deps.settings import SettingsDep, SettingsType
from fastapi_oracle_test_stuff.models import Author


class AuthorService:
    def __init__(
        self,
        settings: SettingsType,
        session_maker: SessionMakerType,
    ):
        self.settings = settings
        self.session_maker = session_maker

    async def get_authors(self) -> list[Author]:
        async with self.session_maker() as session:
            result = await session.execute(select(Author))
            return list(result.scalars())


class AuthorServiceInjectable(AuthorService):
    def __init__(
        self,
        settings: SettingsDep,
        session_maker: SessionMakerDep,
    ):
        super().__init__(settings=settings, session_maker=session_maker)


AuthorServiceDep = Annotated[AuthorService, Depends(AuthorServiceInjectable)]
