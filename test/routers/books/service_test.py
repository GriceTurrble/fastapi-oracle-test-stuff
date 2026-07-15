from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.routers.books import service as book_service

pytestmark = pytest.mark.anyio


class TestGetBooks:
    async def test_returns_books_from_query_results(
        self, service, mock_session, book_factory
    ):
        book_1 = book_factory(id=1)
        book_2 = book_factory(id=2)
        result = MagicMock()
        result.scalars.return_value = [book_1, book_2]
        mock_session.execute.return_value = result

        books = await service.get_books()

        assert books == [book_1, book_2]
        mock_session.execute.assert_awaited_once()

    async def test_returns_empty_list_when_no_books(self, service, mock_session):
        result = MagicMock()
        result.scalars.return_value = []
        mock_session.execute.return_value = result

        books = await service.get_books()

        assert books == []


class TestGetBook:
    async def test_returns_book_when_found(self, service, mock_session, book_factory):
        book = book_factory(id=10)
        mock_session.get.return_value = book

        result = await service.get_book(id=10)

        assert result is book
        args, kwargs = mock_session.get.await_args
        assert args[:2] == (models.Book, 10)
        assert "options" in kwargs

    async def test_returns_none_when_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.get_book(id=999)

        assert result is None


class TestCreateBook:
    async def test_adds_commits_refreshes_and_returns_book(self, service, mock_session):
        data = models.BookCreate(title="Emma", author_id=1, published_year=1815)

        result = await service.create_book(data)

        mock_session.add.assert_called_once()
        added = mock_session.add.call_args.args[0]
        assert isinstance(added, models.Book)
        assert added.title == "Emma"
        assert added.author_id == 1
        assert added.published_year == 1815
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(added, attribute_names=["author"])
        assert result is added


class TestUpdateBook:
    async def test_updates_only_provided_fields(
        self, service, mock_session, book_factory
    ):
        book = book_factory(id=10, title="Old Title", published_year=1813)
        mock_session.get.return_value = book

        result = await service.update_book(
            id=10, data=models.BookUpdate(title="New Title")
        )

        assert result is book
        assert book.title == "New Title"
        assert book.published_year == 1813
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(book, attribute_names=["author"])

    async def test_returns_none_when_book_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.update_book(id=999, data=models.BookUpdate(title="X"))

        assert result is None
        mock_session.commit.assert_not_awaited()


class TestDeleteBook:
    async def test_deletes_and_returns_true_when_found(
        self, service, mock_session, book_factory
    ):
        book = book_factory(id=10)
        mock_session.get.return_value = book

        result = await service.delete_book(id=10)

        assert result is True
        mock_session.delete.assert_awaited_once_with(book)
        mock_session.commit.assert_awaited_once()

    async def test_returns_false_when_not_found(self, service, mock_session):
        mock_session.get.return_value = None

        result = await service.delete_book(id=999)

        assert result is False
        mock_session.delete.assert_not_awaited()
        mock_session.commit.assert_not_awaited()


class TestBookServiceInjectable:
    def test_wires_session_maker_via_base_class(self, mock_session_maker):
        """Covers the one line neither the router tests nor the tests above
        touch: `BookServiceInjectable.__init__` is what FastAPI's
        `Depends()` actually calls in production, but router tests override
        it entirely (see `test/routers/books/conftest.py`) and the tests
        above construct the base `BookService` directly. Calling it here is
        a plain Python call -- the `SessionMakerDep` annotation on its
        `session_maker` parameter only matters when FastAPI parses the
        signature, so this doesn't touch settings or a real DB session.
        """
        injectable = book_service.BookServiceInjectable(
            session_maker=mock_session_maker
        )

        assert injectable.session_maker is mock_session_maker
