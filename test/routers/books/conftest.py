"""Isolates the books router from the real `BookService`."""

from __future__ import annotations

from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

from fastapi_oracle_test_stuff.routers.books import service as book_service


@pytest.fixture
def mock_book_service():
    """An autospecced mock of `BookService`.

    Its async methods become `AsyncMock`s and calls are checked against the
    real method signatures, so a test that calls `get_book(1)` instead of
    `get_book(id=1)` fails loudly instead of silently mismatching the
    router's real usage.
    """
    return create_autospec(book_service.BookService, instance=True)


@pytest.fixture
def client(app, mock_book_service):
    """A `TestClient` with `BookServiceInjectable` overridden to the mock.

    `BookServiceInjectable` is the callable actually passed to `Depends()`,
    so overriding it bypasses `SettingsDep`/`SessionMakerDep` entirely -- no
    settings or DB session is ever constructed for these tests.
    """
    app.dependency_overrides[book_service.BookServiceInjectable] = lambda: (
        mock_book_service
    )
    return TestClient(app)
