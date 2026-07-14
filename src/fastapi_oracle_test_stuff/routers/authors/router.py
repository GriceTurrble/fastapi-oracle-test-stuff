"""Router for authors."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_authors():
    return {"authors": []}
