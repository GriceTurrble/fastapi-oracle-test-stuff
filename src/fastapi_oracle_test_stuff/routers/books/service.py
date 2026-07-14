from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.deps import db, settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BookService:
    def __init__(
        self,
        app_settings: settings.SettingsType,
        session_maker: db.SessionMakerType,
    ):
        self.settings = app_settings
        self.session_maker = session_maker

    @staticmethod
    async def _get(session: AsyncSession, id: int) -> models.Book | None:
        return await session.get(
            models.Book, id, options=[selectinload(models.Book.author)]
        )

    async def get_books(self) -> list[models.Book]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(models.Book).options(selectinload(models.Book.author))
            )
            return list(result.scalars())

    async def get_book(self, id: int) -> models.Book | None:
        async with self.session_maker() as session:
            book = await self._get(session, id)
        return book

    async def create_book(self, data: models.BookCreate) -> models.Book:
        async with self.session_maker() as session:
            book = models.Book(
                title=data.title,
                author_id=data.author_id,
                published_year=data.published_year,
            )
            session.add(book)
            await session.commit()
            await session.refresh(book, attribute_names=["author"])
        return book

    async def update_book(self, id: int, data: models.BookUpdate) -> models.Book | None:
        async with self.session_maker() as session:
            book = await self._get(session, id)
            if book is None:
                return None

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(book, field, value)

            await session.commit()
            await session.refresh(book, attribute_names=["author"])
        return book

    async def delete_book(self, id: int) -> bool:
        async with self.session_maker() as session:
            book = await self._get(session, id)
            if book is None:
                return False

            await session.delete(book)
            await session.commit()
        return True


class BookServiceInjectable(BookService):
    def __init__(
        self,
        app_settings: settings.SettingsDep,
        session_maker: db.SessionMakerDep,
    ):
        super().__init__(app_settings=app_settings, session_maker=session_maker)


BookServiceDep = Annotated[BookService, Depends(BookServiceInjectable)]
