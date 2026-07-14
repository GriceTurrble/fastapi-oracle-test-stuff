from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_oracle_test_stuff.models.db_base import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str | None


class AuthorCreate(BaseModel):
    name: str
    country: str | None = None


class AuthorUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
