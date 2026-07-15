from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from fastapi_oracle_test_stuff import models

pytestmark = pytest.mark.anyio


class TestGetAuthors:
    async def test_returns_authors_from_query_results(
        self, service, mock_session, author_factory
    ):
        author_1 = author_factory(id=1)
        author_2 = author_factory(id=2)
        result = MagicMock()
        result.scalars.return_value = [author_1, author_2]
        mock_session.execute.return_value = result

        authors = await service.get_authors()

        assert authors == [author_1, author_2]
        mock_session.execute.assert_awaited_once()

    async def test_returns_empty_list_when_no_authors(self, service, mock_session):
        result = MagicMock()
        result.scalars.return_value = []
        mock_session.execute.return_value = result

        authors = await service.get_authors()

        assert authors == []


class TestGetAuthor:
    async def test_returns_author_when_found(
        self, service, mock_session, author_factory
    ):
        author = author_factory(id=1)
        mock_session.get.return_value = author

        result = await service.get_author(id=1)

        assert result is author
        args, kwargs = mock_session.get.await_args
        assert args[:2] == (models.Author, 1)
        assert "options" in kwargs

    async def test_returns_none_when_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.get_author(id=999)

        assert result is None


class TestCreateAuthor:
    async def test_adds_commits_refreshes_and_returns_author(
        self, service, mock_session
    ):
        data = models.AuthorCreate(name="New Author", country="Canada")

        result = await service.create_author(data)

        mock_session.add.assert_called_once()
        added = mock_session.add.call_args.args[0]
        assert isinstance(added, models.Author)
        assert added.name == "New Author"
        assert added.country == "Canada"
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(added, attribute_names=["books"])
        assert result is added


class TestUpdateAuthor:
    async def test_updates_only_provided_fields(
        self, service, mock_session, author_factory
    ):
        author = author_factory(id=1, name="Old Name", country="United Kingdom")
        mock_session.get.return_value = author

        result = await service.update_author(
            id=1, data=models.AuthorUpdate(name="New Name")
        )

        assert result is author
        assert author.name == "New Name"
        assert author.country == "United Kingdom"
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(author, attribute_names=["books"])

    async def test_returns_none_when_author_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.update_author(id=999, data=models.AuthorUpdate(name="X"))

        assert result is None
        mock_session.commit.assert_not_awaited()


class TestDeleteAuthor:
    async def test_deletes_and_returns_true_when_found(
        self, service, mock_session, author_factory
    ):
        author = author_factory(id=1)
        mock_session.get.return_value = author

        result = await service.delete_author(id=1)

        assert result is True
        mock_session.delete.assert_awaited_once_with(author)
        mock_session.commit.assert_awaited_once()

    async def test_returns_false_when_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.delete_author(id=999)

        assert result is False
        mock_session.delete.assert_not_awaited()
        mock_session.commit.assert_not_awaited()
