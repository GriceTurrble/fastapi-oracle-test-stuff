set dotenv-load

### START COMMON ###
import? 'common.just'

FASTAPI_APP_PATH := "fastapi_oracle_test_stuff.main:create_app"

# Show these help docs
help:
    @just --list --unsorted --justfile {{ source_file() }}

# Pull latest common justfile recipes to local repo
[group("commons")]
sync-commons:
    -rm common.just
    curl -H 'Cache-Control: no-cache, no-store' \
        https://raw.githubusercontent.com/griceturrble/common-project-files/main/common.just?cachebust={{ uuid() }} > common.just
### END COMMON ###

# bootstrap the dev environment
bootstrap:
    just sync-commons
    just bootstrap-commons
    just sync

# Sync uv dependencies in all groups
sync:
    uv sync --all-groups

# Run tests
test:
    uv run pytest

# Start docker compose services
up:
    docker compose up -d

# Stop docker compose services
down:
    docker compose down

# Seed the local Oracle DB with dummy data
db-seed:
    docker compose exec -T oracle-db sqlplus -s \
        "$TESTTHING__DB__USER/$TESTTHING__DB__PASSWORD@//localhost:1521/$TESTTHING__DB__SERVICE" \
        < sql/seed.sql

# Run API in granian in local shell, outside docker compose
run-local:
    uv run granian \
        --interface asgi \
        --reload \
        --factory \
        {{FASTAPI_APP_PATH}}

# Reload the running docker compose app for the FastAPI service, without stopping the DB
reload-docker-compose-app:
    docker compose build app
    docker compose up -d app

alias reload-app := reload-docker-compose-app
