set dotenv-load

### START COMMON ###
import? 'common.just'

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

# Serve docs/ as a mkdocs site locally with hot-reloading
docs:
    uv run mkdocs serve

# Start services
up:
    docker compose up

# Seed the local Oracle DB with dummy data
db-seed:
    docker compose exec -T oracle-db sqlplus -s \
        "$TESTTHING__DB__USER/$TESTTHING__DB__PASSWORD@//localhost:1521/$TESTTHING__DB__SERVICE" \
        < sql/seed.sql
