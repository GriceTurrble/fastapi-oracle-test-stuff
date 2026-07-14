"""Router for books."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.routers.books import service as book_service

router = APIRouter()


def _book_not_found(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book {id} not found",
    )


@router.get("/", response_model=list[models.BookRead])
async def list_books(service: book_service.BookServiceDep):
    books = await service.get_books()
    return [models.BookRead.model_validate(book) for book in books]


@router.get("/{id}", response_model=models.BookRead)
async def get_book(id: int, service: book_service.BookServiceDep):
    book = await service.get_book(id=id)
    if book is None:
        raise _book_not_found(id)

    return models.BookRead.model_validate(book)


@router.post("/", response_model=models.BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(data: models.BookCreate, service: book_service.BookServiceDep):
    book = await service.create_book(data)
    return models.BookRead.model_validate(book)


@router.patch("/{id}", response_model=models.BookRead)
async def update_book(
    id: int, data: models.BookUpdate, service: book_service.BookServiceDep
):
    book = await service.update_book(id=id, data=data)
    if book is None:
        raise _book_not_found(id)

    return models.BookRead.model_validate(book)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, service: book_service.BookServiceDep):
    deleted = await service.delete_book(id=id)
    if not deleted:
        raise _book_not_found(id)
