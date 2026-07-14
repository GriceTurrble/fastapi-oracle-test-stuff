"""Router for authors."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from fastapi_oracle_test_stuff import models
from fastapi_oracle_test_stuff.routers.authors import service as author_service

router = APIRouter()


def _author_not_found(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Author {id} not found",
    )


@router.get("/", response_model=list[models.AuthorRead])
async def list_authors(service: author_service.AuthorServiceDep):
    authors = await service.get_authors()
    return [models.AuthorRead.model_validate(author) for author in authors]


@router.get("/{id}", response_model=models.AuthorRead)
async def get_author(id: int, service: author_service.AuthorServiceDep):
    author = await service.get_author(id=id)
    if author is None:
        raise _author_not_found(id)

    return models.AuthorRead.model_validate(author)


@router.post("/", response_model=models.AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: models.AuthorCreate, service: author_service.AuthorServiceDep
):
    author = await service.create_author(data)
    return models.AuthorRead.model_validate(author)


@router.patch("/{id}", response_model=models.AuthorRead)
async def update_author(
    id: int, data: models.AuthorUpdate, service: author_service.AuthorServiceDep
):
    author = await service.update_author(id=id, data=data)
    if author is None:
        raise _author_not_found(id)

    return models.AuthorRead.model_validate(author)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(id: int, service: author_service.AuthorServiceDep):
    deleted = await service.delete_author(id=id)
    if not deleted:
        raise _author_not_found(id)
