"""Isolates the authors router from the real `AuthorService`."""

from __future__ import annotations

from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

from fastapi_oracle_test_stuff.routers.authors import service as author_service


@pytest.fixture
def mock_author_service():
    """An autospecced mock of `AuthorService`.

    Its async methods become `AsyncMock`s and calls are checked against the
    real method signatures, so a test that calls `get_author(1)` instead of
    `get_author(id=1)` fails loudly instead of silently mismatching the
    router's real usage.
    """
    return create_autospec(author_service.AuthorService, instance=True)


@pytest.fixture
def client(app, mock_author_service):
    """A `TestClient` with `AuthorServiceInjectable` overridden to the mock.

    `AuthorServiceInjectable` is the callable actually passed to `Depends()`,
    so overriding it bypasses `SettingsDep`/`SessionMakerDep` entirely -- no
    settings or DB session is ever constructed for these tests.
    """
    app.dependency_overrides[author_service.AuthorServiceInjectable] = lambda: (
        mock_author_service
    )
    return TestClient(app)
