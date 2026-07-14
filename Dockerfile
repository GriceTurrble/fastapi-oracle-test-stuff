FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project --no-dev

COPY src ./src
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "--locked", "granian", "--interface", "asgi", "--factory", "--host", "0.0.0.0", "--port", "8000", "fastapi_oracle_test_stuff.main:create_app"]
