"""Router for authors."""

from __future__ import annotations

from fastapi import APIRouter

from fastapi_oracle_test_stuff.models import AuthorRead
from fastapi_oracle_test_stuff.routers.authors.service import AuthorServiceDep

router = APIRouter()


@router.get("/", response_model=list[AuthorRead])
async def list_authors(service: AuthorServiceDep):
    authors = await service.get_authors()
    return [AuthorRead.model_validate(author) for author in authors]
