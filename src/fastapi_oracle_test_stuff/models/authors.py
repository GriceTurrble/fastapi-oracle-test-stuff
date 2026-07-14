from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_oracle_test_stuff.models.db_base import Base

if TYPE_CHECKING:
    from fastapi_oracle_test_stuff.models.books import Book


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))

    books: Mapped[list[Book]] = relationship(back_populates="author")


class BookSummary(BaseModel):
    """A Book, as embedded in an AuthorRead's `books` list."""

    id: int
    title: str
    published_year: int | None
    url: str


class AuthorRead(BaseModel):
    id: int
    name: str
    country: str | None
    books: list[BookSummary]


class AuthorCreate(BaseModel):
    name: str
    country: str | None = None


class AuthorUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
