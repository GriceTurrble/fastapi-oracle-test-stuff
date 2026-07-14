from __future__ import annotations

from fastapi import APIRouter

from .authors.router import router as authors_router
from .books.router import router as books_router

main_router = APIRouter()
main_router.include_router(authors_router, prefix="/authors", tags=["authors"])
main_router.include_router(books_router, prefix="/books", tags=["books"])
