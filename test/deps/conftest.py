"""Fixtures isolating `deps.db` tests from real settings and cached state."""

from __future__ import annotations

import pytest

from fastapi_oracle_test_stuff.deps import db
from fastapi_oracle_test_stuff.deps.settings import DBSettings, Settings


@pytest.fixture(autouse=True)
def _reset_session_maker_cache():
    """Clear `db._session_maker_cache` before and after every test.

    The cache is module-level global state keyed by a constant string, so
    without resetting it, whichever test runs first would "win" and every
    later test would see its cached `async_sessionmaker` instead of its own.
    """
    db._async_session_maker_cache.clear()
    yield
    db._async_session_maker_cache.clear()


@pytest.fixture
def settings_factory():
    """Build a `Settings` instance without touching real env vars.

    All fields are passed explicitly, which pydantic-settings treats as the
    highest-priority source -- so this works the same whether or not
    `TESTTHING__*` env vars happen to be set in the process.
    """

    def _make(
        *,
        user: str = "test_user",
        password: str = "test_password",  # noqa: S107
        host: str = "test_host",
        port: int = 1521,
        service: str = "test_service",
    ) -> Settings:
        return Settings(
            db=DBSettings(
                user=user,
                password=password,
                host=host,
                port=port,
                service=service,
            )
        )

    return _make
