"""Shared fixtures for the whole test suite.

Router tests get a real `TestClient` wired to a real `FastAPI` app, but with
the service-layer dependencies overridden by mocks (see the `conftest.py`
files under `test/routers/`) so no settings or database session are ever
constructed. Service-layer tests go one level down: they exercise the real
service classes wired to a mocked `AsyncSession`/session maker (see
`mock_session`/`mock_session_maker` below), so no settings or real database
connection are needed there either.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.main import create_app


@pytest.fixture
def anyio_backend():
    """Run anyio-marked async tests (e.g. service-layer tests) on asyncio."""
    return "asyncio"


@pytest.fixture
def app():
    """A fresh FastAPI app per test, so dependency overrides never leak."""
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def author_factory():
    """Build a transient `models.Author` ORM instance, not backed by a session."""

    def _make(
        *,
        id: int = 1,
        name: str = "Jane Austen",
        country: str | None = "United Kingdom",
        books: list[models.Book] | None = None,
    ) -> models.Author:
        author = models.Author(id=id, name=name, country=country)
        author.books = books if books is not None else []
        return author

    return _make


@pytest.fixture
def book_factory(author_factory):
    """Build a transient `models.Book` ORM instance, not backed by a session."""

    def _make(
        *,
        id: int = 1,
        title: str = "Pride and Prejudice",
        published_year: int | None = 1813,
        author: models.Author | None = None,
    ) -> models.Book:
        if author is None:
            author = author_factory(books=[])
        book = models.Book(
            id=id,
            title=title,
            author_id=author.id,
            published_year=published_year,
        )
        book.author = author
        return book

    return _make


@pytest.fixture
def mock_session():
    """A `MagicMock(spec=AsyncSession)`, usable as `async with mock_session as s`.

    Spec'ing on `AsyncSession` auto-configures its async methods (`execute`,
    `get`, `commit`, `refresh`, `delete`, ...) as `AsyncMock`s while sync ones
    (`add`) stay plain `MagicMock`s. `__aenter__` doesn't return `self` by
    default though, so it's wired up explicitly here to match how the service
    layer actually uses it: `async with self.async_session_maker() as session:`.
    """
    session = MagicMock(spec=AsyncSession)
    session.__aenter__.return_value = session
    session.__aexit__.return_value = False
    return session


@pytest.fixture
def mock_session_maker(mock_session):
    """A stand-in for `async_sessionmaker`, returning `mock_session` when called.

    The real `async_sessionmaker.__call__()` returns an `AsyncSession`
    directly -- that session is itself the async context manager -- so this
    just needs to be a plain callable returning `mock_session`.
    """
    return MagicMock(return_value=mock_session)
