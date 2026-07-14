from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_oracle_test_stuff.models.db_base import Base

if TYPE_CHECKING:
    from fastapi_oracle_test_stuff.models.authors import Author


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    published_year: Mapped[int | None]

    author: Mapped[Author] = relationship(back_populates="books")


class AuthorSummary(BaseModel):
    """An Author, as embedded in a BookRead's `author` field."""

    id: int
    name: str
    country: str | None
    url: str


class BookRead(BaseModel):
    id: int
    title: str
    published_year: int | None
    author: AuthorSummary


class BookCreate(BaseModel):
    title: str
    author_id: int
    published_year: int | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author_id: int | None = None
    published_year: int | None = None
