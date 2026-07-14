"""Router for books."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_books():
    return {"books": []}
