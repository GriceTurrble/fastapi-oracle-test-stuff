from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.deps import db, settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AuthorService:
    def __init__(
        self,
        app_settings: settings.SettingsType,
        session_maker: db.SessionMakerType,
    ):
        self.settings = app_settings
        self.session_maker = session_maker

    @staticmethod
    async def _get(session: AsyncSession, id: int) -> models.Author | None:
        return await session.get(
            models.Author,
            id,
            options=[selectinload(models.Author.books)],
        )

    async def get_authors(self) -> list[models.Author]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(models.Author).options(selectinload(models.Author.books))
            )
            return list(result.scalars())

    async def get_author(self, id: int) -> models.Author | None:
        async with self.session_maker() as session:
            author = await self._get(session, id)
        return author

    async def create_author(self, data: models.AuthorCreate) -> models.Author:
        async with self.session_maker() as session:
            author = models.Author(name=data.name, country=data.country)
            session.add(author)
            await session.commit()
            await session.refresh(author, attribute_names=["books"])
        return author

    async def update_author(
        self, id: int, data: models.AuthorUpdate
    ) -> models.Author | None:
        async with self.session_maker() as session:
            author = await self._get(session, id)
            if author is None:
                return None

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(author, field, value)

            await session.commit()
            await session.refresh(author, attribute_names=["books"])
        return author

    async def delete_author(self, id: int) -> bool:
        async with self.session_maker() as session:
            author = await self._get(session, id)
            if author is None:
                return False

            await session.delete(author)
            await session.commit()
        return True


class AuthorServiceInjectable(AuthorService):
    def __init__(
        self,
        app_settings: settings.SettingsDep,
        session_maker: db.SessionMakerDep,
    ):
        super().__init__(app_settings=app_settings, session_maker=session_maker)


AuthorServiceDep = Annotated[AuthorService, Depends(AuthorServiceInjectable)]
