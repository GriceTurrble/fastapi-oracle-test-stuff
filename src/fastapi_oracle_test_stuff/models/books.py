from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_oracle_test_stuff.models.db_base import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    published_year: Mapped[int | None]


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author_id: int
    published_year: int | None


class BookCreate(BaseModel):
    title: str
    author_id: int
    published_year: int | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author_id: int | None = None
    published_year: int | None = None
