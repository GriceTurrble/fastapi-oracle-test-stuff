"""Router for books."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.routers.books import service as book_service

router = APIRouter()


def _book_not_found(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book {id} not found",
    )


def to_book_response(
    book: models.Book,
    request: Request,
) -> models.BookRead:
    return models.BookRead(
        id=book.id,
        title=book.title,
        published_year=book.published_year,
        author=models.BookAuthorSummary(
            id=book.author.id,
            name=book.author.name,
            country=book.author.country,
            url=str(request.url_for("get_author", id=book.author.id)),
        ),
    )


@router.get(
    "/",
    response_model=list[models.BookRead],
)
async def list_books(
    request: Request,
    service: book_service.BookServiceDep,
):
    books = await service.get_books()
    return [to_book_response(book, request) for book in books]


@router.get(
    "/{id}",
    response_model=models.BookRead,
)
async def get_book(
    id: int,
    request: Request,
    service: book_service.BookServiceDep,
):
    book = await service.get_book(id=id)
    if book is None:
        raise _book_not_found(id)

    return to_book_response(book, request)


@router.post(
    "/",
    response_model=models.BookRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    data: models.BookCreate,
    request: Request,
    service: book_service.BookServiceDep,
):
    book = await service.create_book(data)
    return to_book_response(book, request)


@router.patch(
    "/{id}",
    response_model=models.BookRead,
)
async def update_book(
    id: int,
    data: models.BookUpdate,
    request: Request,
    service: book_service.BookServiceDep,
):
    book = await service.update_book(id=id, data=data)
    if book is None:
        raise _book_not_found(id)

    return to_book_response(book, request)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    id: int,
    service: book_service.BookServiceDep,
):
    deleted = await service.delete_book(id=id)
    if not deleted:
        raise _book_not_found(id)
