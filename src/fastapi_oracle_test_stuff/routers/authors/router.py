"""Router for authors."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_oracle_test_stuff.models import authors as author_models
from fastapi_oracle_test_stuff.models import books as book_models
from fastapi_oracle_test_stuff.routers.authors import service as author_service
from fastapi_oracle_test_stuff.routers.books.router import to_book_response

router = APIRouter()


def _author_not_found(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Author {id} not found",
    )


def to_author_response(
    author: author_models.Author,
    request: Request,
) -> author_models.AuthorRead:
    return author_models.AuthorRead(
        id=author.id,
        name=author.name,
        country=author.country,
        books=[
            author_models.AuthorBookSummary(
                id=book.id,
                title=book.title,
                published_year=book.published_year,
                url=str(request.url_for("get_book", id=book.id)),
            )
            for book in author.books
        ],
    )


@router.get(
    "/",
    response_model=list[author_models.AuthorRead],
)
async def list_authors(
    request: Request,
    service: author_service.AuthorServiceDep,
):
    authors = await service.get_authors()
    return [to_author_response(author, request) for author in authors]


@router.get(
    "/{id}",
    response_model=author_models.AuthorRead,
)
async def get_author(
    id: int,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.get_author(id=id)
    if author is None:
        raise _author_not_found(id)

    return to_author_response(author, request)


@router.get(
    "/{id}/books",
    response_model=list[book_models.BookRead],
)
async def list_author_books(
    id: int,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.get_author(id=id)
    if author is None:
        raise _author_not_found(id)

    return [to_book_response(book, request) for book in author.books]


@router.post(
    "/",
    response_model=author_models.AuthorRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    data: author_models.AuthorCreate,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.create_author(data)
    return to_author_response(author, request)


@router.patch(
    "/{id}",
    response_model=author_models.AuthorRead,
)
async def update_author(
    id: int,
    data: author_models.AuthorUpdate,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.update_author(id=id, data=data)
    if author is None:
        raise _author_not_found(id)

    return to_author_response(author, request)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    id: int,
    service: author_service.AuthorServiceDep,
):
    deleted = await service.delete_author(id=id)
    if not deleted:
        raise _author_not_found(id)
