from __future__ import annotations

from fastapi import FastAPI

from fastapi_oracle_test_stuff.routers import main_router

API_PREFIX = "/api"
DOCS_URL = f"{API_PREFIX}/docs"
REDOC_URL = f"{API_PREFIX}/redoc"
OPENAPI_URL = f"{API_PREFIX}/openapi.json"


def create_app():
    app = FastAPI(
        title="Books and Authors demo API",
        docs_url=DOCS_URL,
        redoc_url=DOCS_URL,
        openapi_url=OPENAPI_URL,
    )

    app.include_router(main_router, prefix=API_PREFIX)

    return app
