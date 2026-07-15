from __future__ import annotations

from fastapi_oracle_test_stuff import models


class TestListBooks:
    def test_returns_books_from_service(self, client, mock_book_service, book_factory):
        book = book_factory(id=10, title="Pride and Prejudice", published_year=1813)

        mock_book_service.get_books.return_value = [book]

        response = client.get("/api/books/")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 10,
                "title": "Pride and Prejudice",
                "published_year": 1813,
                "author": {
                    "id": 1,
                    "name": "Jane Austen",
                    "country": "United Kingdom",
                    "url": "http://testserver/api/authors/1",
                },
            }
        ]
        mock_book_service.get_books.assert_awaited_once_with()

    def test_returns_empty_list_when_no_books(self, client, mock_book_service):
        mock_book_service.get_books.return_value = []

        response = client.get("/api/books/")

        assert response.status_code == 200
        assert response.json() == []


class TestGetBook:
    def test_returns_book_when_found(self, client, mock_book_service, book_factory):
        book = book_factory(id=10, title="Pride and Prejudice", published_year=1813)
        mock_book_service.get_book.return_value = book

        response = client.get("/api/books/10")

        assert response.status_code == 200
        assert response.json() == {
            "id": 10,
            "title": "Pride and Prejudice",
            "published_year": 1813,
            "author": {
                "id": 1,
                "name": "Jane Austen",
                "country": "United Kingdom",
                "url": "http://testserver/api/authors/1",
            },
        }
        mock_book_service.get_book.assert_awaited_once_with(id=10)

    def test_returns_404_when_not_found(self, client, mock_book_service):
        mock_book_service.get_book.return_value = None

        response = client.get("/api/books/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Book 999 not found"}
        mock_book_service.get_book.assert_awaited_once_with(id=999)


class TestCreateBook:
    def test_creates_book_and_returns_201(
        self, client, mock_book_service, book_factory
    ):
        created = book_factory(id=20, title="Emma", published_year=1815)
        mock_book_service.create_book.return_value = created

        response = client.post(
            "/api/books/",
            json={"title": "Emma", "author_id": 1, "published_year": 1815},
        )

        assert response.status_code == 201
        assert response.json()["id"] == 20
        mock_book_service.create_book.assert_awaited_once_with(
            models.BookCreate(title="Emma", author_id=1, published_year=1815)
        )

    def test_creates_book_without_published_year(
        self, client, mock_book_service, book_factory
    ):
        created = book_factory(id=20, title="Emma", published_year=None)
        mock_book_service.create_book.return_value = created

        response = client.post("/api/books/", json={"title": "Emma", "author_id": 1})

        assert response.status_code == 201
        mock_book_service.create_book.assert_awaited_once_with(
            models.BookCreate(title="Emma", author_id=1, published_year=None)
        )


class TestUpdateBook:
    def test_updates_book_when_found(self, client, mock_book_service, book_factory):
        updated = book_factory(id=10, title="Updated Title", published_year=1813)
        mock_book_service.update_book.return_value = updated

        response = client.patch("/api/books/10", json={"title": "Updated Title"})

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        mock_book_service.update_book.assert_awaited_once_with(
            id=10, data=models.BookUpdate(title="Updated Title")
        )

    def test_returns_404_when_not_found(self, client, mock_book_service):
        mock_book_service.update_book.return_value = None

        response = client.patch("/api/books/999", json={"title": "X"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Book 999 not found"}
        mock_book_service.update_book.assert_awaited_once_with(
            id=999, data=models.BookUpdate(title="X")
        )


class TestDeleteBook:
    def test_deletes_book_when_found(self, client, mock_book_service):
        mock_book_service.delete_book.return_value = True

        response = client.delete("/api/books/10")

        assert response.status_code == 204
        assert response.content == b""
        mock_book_service.delete_book.assert_awaited_once_with(id=10)

    def test_returns_404_when_not_found(self, client, mock_book_service):
        mock_book_service.delete_book.return_value = False

        response = client.delete("/api/books/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Book 999 not found"}
