"""Router for authors."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.routers.authors import service as author_service

router = APIRouter()


def _author_not_found(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Author {id} not found",
    )


def _to_author_response(author: models.Author, request: Request) -> models.AuthorRead:
    return models.AuthorRead(
        id=author.id,
        name=author.name,
        country=author.country,
        books=[
            models.BookSummary(
                id=book.id,
                title=book.title,
                published_year=book.published_year,
                url=str(request.url_for("get_book", id=book.id)),
            )
            for book in author.books
        ],
    )


@router.get("/", response_model=list[models.AuthorRead])
async def list_authors(request: Request, service: author_service.AuthorServiceDep):
    authors = await service.get_authors()
    return [_to_author_response(author, request) for author in authors]


@router.get("/{id}", response_model=models.AuthorRead)
async def get_author(
    id: int, request: Request, service: author_service.AuthorServiceDep
):
    author = await service.get_author(id=id)
    if author is None:
        raise _author_not_found(id)

    return _to_author_response(author, request)


@router.post("/", response_model=models.AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: models.AuthorCreate,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.create_author(data)
    return _to_author_response(author, request)


@router.patch("/{id}", response_model=models.AuthorRead)
async def update_author(
    id: int,
    data: models.AuthorUpdate,
    request: Request,
    service: author_service.AuthorServiceDep,
):
    author = await service.update_author(id=id, data=data)
    if author is None:
        raise _author_not_found(id)

    return _to_author_response(author, request)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(id: int, service: author_service.AuthorServiceDep):
    deleted = await service.delete_author(id=id)
    if not deleted:
        raise _author_not_found(id)
