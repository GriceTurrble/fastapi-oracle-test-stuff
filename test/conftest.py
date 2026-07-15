"""Shared fixtures for the whole test suite.

Router tests get a real `TestClient` wired to a real `FastAPI` app, but with
the service-layer dependencies overridden by mocks (see the `conftest.py`
files under `test/routers/`) so no settings or database session are ever
constructed.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

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
