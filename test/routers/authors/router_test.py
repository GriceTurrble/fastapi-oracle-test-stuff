from __future__ import annotations

from fastapi_oracle_test_stuff import models


class TestListAuthors:
    def test_returns_authors_from_service(
        self, client, mock_author_service, author_factory, book_factory
    ):
        author = author_factory(id=1, name="Jane Austen", country="United Kingdom")
        book = book_factory(
            id=10, title="Pride and Prejudice", published_year=1813, author=author
        )
        author.books = [book]
        mock_author_service.get_authors.return_value = [author]

        response = client.get("/api/authors/")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "name": "Jane Austen",
                "country": "United Kingdom",
                "books": [
                    {
                        "id": 10,
                        "title": "Pride and Prejudice",
                        "published_year": 1813,
                        "url": "http://testserver/api/books/10",
                    }
                ],
            }
        ]
        mock_author_service.get_authors.assert_awaited_once_with()

    def test_returns_empty_list_when_no_authors(self, client, mock_author_service):
        mock_author_service.get_authors.return_value = []

        response = client.get("/api/authors/")

        assert response.status_code == 200
        assert response.json() == []


class TestGetAuthor:
    def test_returns_author_when_found(
        self, client, mock_author_service, author_factory
    ):
        author = author_factory(id=1, name="Jane Austen", country="United Kingdom")
        mock_author_service.get_author.return_value = author

        response = client.get("/api/authors/1")

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Jane Austen",
            "country": "United Kingdom",
            "books": [],
        }
        mock_author_service.get_author.assert_awaited_once_with(id=1)

    def test_returns_404_when_not_found(self, client, mock_author_service):
        mock_author_service.get_author.return_value = None

        response = client.get("/api/authors/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Author 999 not found"}
        mock_author_service.get_author.assert_awaited_once_with(id=999)


class TestListAuthorBooks:
    def test_returns_books_when_author_found(
        self, client, mock_author_service, author_factory, book_factory
    ):
        author = author_factory(id=1)
        book = book_factory(id=10, author=author)
        author.books = [book]
        mock_author_service.get_author.return_value = author

        response = client.get("/api/authors/1/books")

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
        mock_author_service.get_author.assert_awaited_once_with(id=1)

    def test_returns_404_when_author_not_found(self, client, mock_author_service):
        mock_author_service.get_author.return_value = None

        response = client.get("/api/authors/999/books")

        assert response.status_code == 404
        assert response.json() == {"detail": "Author 999 not found"}


class TestCreateAuthor:
    def test_creates_author_and_returns_201(
        self, client, mock_author_service, author_factory
    ):
        created = author_factory(id=5, name="New Author", country="Canada")
        mock_author_service.create_author.return_value = created

        response = client.post(
            "/api/authors/",
            json={"name": "New Author", "country": "Canada"},
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": 5,
            "name": "New Author",
            "country": "Canada",
            "books": [],
        }
        mock_author_service.create_author.assert_awaited_once_with(
            models.AuthorCreate(name="New Author", country="Canada")
        )

    def test_creates_author_without_country(
        self, client, mock_author_service, author_factory
    ):
        created = author_factory(id=5, name="New Author", country=None)
        mock_author_service.create_author.return_value = created

        response = client.post("/api/authors/", json={"name": "New Author"})

        assert response.status_code == 201
        mock_author_service.create_author.assert_awaited_once_with(
            models.AuthorCreate(name="New Author", country=None)
        )


class TestUpdateAuthor:
    def test_updates_author_when_found(
        self, client, mock_author_service, author_factory
    ):
        updated = author_factory(id=1, name="Updated Name", country="United Kingdom")
        mock_author_service.update_author.return_value = updated

        response = client.patch("/api/authors/1", json={"name": "Updated Name"})

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        mock_author_service.update_author.assert_awaited_once_with(
            id=1, data=models.AuthorUpdate(name="Updated Name")
        )

    def test_returns_404_when_not_found(self, client, mock_author_service):
        mock_author_service.update_author.return_value = None

        response = client.patch("/api/authors/999", json={"name": "X"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Author 999 not found"}
        mock_author_service.update_author.assert_awaited_once_with(
            id=999, data=models.AuthorUpdate(name="X")
        )


class TestDeleteAuthor:
    def test_deletes_author_when_found(self, client, mock_author_service):
        mock_author_service.delete_author.return_value = True

        response = client.delete("/api/authors/1")

        assert response.status_code == 204
        assert response.content == b""
        mock_author_service.delete_author.assert_awaited_once_with(id=1)

    def test_returns_404_when_not_found(self, client, mock_author_service):
        mock_author_service.delete_author.return_value = False

        response = client.delete("/api/authors/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Author 999 not found"}
