from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker

from fastapi_oracle_test_stuff.deps import db


class TestBuildSessionMaker:
    def test_returns_an_async_sessionmaker(self, settings_factory):
        session_maker = db._build_async_session_maker(settings_factory())

        assert isinstance(session_maker, async_sessionmaker)

    def test_configures_engine_from_settings(self, settings_factory):
        settings = settings_factory(
            user="oracle_user",
            password="s3cret",  # noqa: S106
            host="oracle.example.com",
            port=1522,
            service="orclpdb",
        )

        session_maker = db._build_async_session_maker(settings)

        url = session_maker.kw["bind"].url
        assert url.drivername == "oracle+oracledb"
        assert url.username == "oracle_user"
        assert url.password == "s3cret"  # noqa: S105
        assert url.host == "oracle.example.com"
        assert url.port == 1522
        assert url.query["service_name"] == "orclpdb"

    def test_disables_expire_on_commit(self, settings_factory):
        session_maker = db._build_async_session_maker(settings_factory())

        assert session_maker.kw["expire_on_commit"] is False

    def test_caches_the_session_maker_across_calls(self, settings_factory):
        settings = settings_factory()

        first = db._build_async_session_maker(settings)
        second = db._build_async_session_maker(settings)

        assert first is second

    def test_ignores_new_settings_once_cached(self, settings_factory):
        """The cache key is the constant string "default", not the settings
        passed in, so a second call with different settings still returns
        the session maker built from the *first* call's settings. This is
        surprising enough to pin down with a test: it means settings changes
        won't take effect without a process restart.
        """
        first_settings = settings_factory(host="first-host")
        second_settings = settings_factory(host="second-host")

        first = db._build_async_session_maker(first_settings)
        second = db._build_async_session_maker(second_settings)

        assert first is second
        assert second.kw["bind"].url.host == "first-host"


class TestGetSessionMaker:
    def test_returns_same_session_maker_as_build_session_maker(self, settings_factory):
        settings = settings_factory()

        via_get = db.get_async_session_maker(settings)
        via_build = db._build_async_session_maker(settings)

        assert via_get is via_build
