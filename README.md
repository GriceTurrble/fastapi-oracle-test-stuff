# fastapi-oracle-test-stuff

An example [FastAPI] application backed by a free [Oracle Autonomous Database],
used to try out the connection and libraries for talking to Oracle from Python.

The goal of this repo is working out a **repeatable pattern for routers
and services in FastAPI, built around dependency injection**: how a route
handler, a service class, and the DB session/settings it needs can be wired
together with `Depends()` in a way that's easy to test in isolation at every
layer. An example API for books and authors demonstrates this patterns. See [Design notes](#design-notes) below for how it's put together
and why.

## Development

### Setup

> [!NOTE]
> Run `just` or `just help` to see all available commands.

- On a system using [Homebrew], use the following to install tooling:

  ```shell
  $ brew bundle
  ```

  Otherwise, install the following tools separately as appropriate for your system:

  - [gh], GitHub CLI
  - [just], command runner
  - [pre-commit], project linters run pre-commit and in GitHub Actions CI
  - [uv], for Python project management.

- Run the following to bootstrap the development environment and dependencies:

  ```shell
  just bootstrap
  ```

- Copy `.env.sample` to `.env` and adjust as needed. These values configure
  both the app (`TESTTHING__DB__*` settings, see [Settings](#deps-settingspy--dbpy))
  and the `oracle-db` container in [`compose.yaml`](compose.yaml).

  ```shell
  cp .env.sample .env
  ```

### Running the app

Start the API and its Oracle database together with docker compose:

```shell
just up
```

Then seed some dummy data into the database:

```shell
just db-seed
```

The API is now available at `http://localhost:8000/api`, with interactive
docs at `http://localhost:8000/api/docs`.

After changing code under `src/`, rebuild and restart just the `app`
container without tearing down the database:

```shell
just reload-docker-compose-app
# OR
just reload-app
```

Alternatively, run the API directly on the host (against the `oracle-db`
container still started via `just up`), with autoreload:

```shell
just run-local
```

#### Example requests

```shell
# Create an author
curl -X POST http://localhost:8000/api/authors/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Jane Austen", "country": "United Kingdom"}'

# Create a book for that author
curl -X POST http://localhost:8000/api/books/ \
  -H 'Content-Type: application/json' \
  -d '{"title": "Pride and Prejudice", "published_year": 1813, "author_id": 1}'

# List authors, with their books nested inline
curl http://localhost:8000/api/authors/

# Fetch a single book, with its author nested inline
curl http://localhost:8000/api/books/1
```

### Testing

```shell
just test
```

This runs `pytest` with coverage; an HTML report is written to `pytest_cov/`.

## Design notes

The layout under `src/fastapi_oracle_test_stuff/` is meant to be a template
you can copy per-resource (see `routers/authors/` and `routers/books/`, which
are both structured identically):

```
src/fastapi_oracle_test_stuff/
├── deps/
│   ├── settings.py   # app configuration, sourced from the environment
│   └── db.py         # DB engine / sessionmaker, built from settings
├── models/
│   ├── db_base.py    # shared SQLAlchemy declarative base
│   ├── authors.py    # Author ORM model + its Pydantic read/create/update schemas
│   └── books.py      # Book ORM model + its Pydantic read/create/update schemas
├── routers/
│   ├── authors/
│   │   ├── router.py   # HTTP layer: path operations, request/response shaping
│   │   └── service.py  # business logic: talks to the DB via a session
│   └── books/
│       ├── router.py
│       └── service.py
└── main.py           # creates the FastAPI app, mounts routers
```

### Router/service split

Each resource has a `router.py` and a `service.py`:

- **`service.py`** runs business logic,
  interacts with data sources,
  sends notifications to external services,
  runs calculations,
  etc.
  Relatively "raw" data is returned from this layer,
  usually the SQLAlchemy ORM models that are returned from queries.
- **`router.py`** handles routing logic, request models,
  HTTP status codes, and converting data to response models.
  (see `to_author_response` / `to_book_response`).

A **service** is a plain class, e.g. `AuthorService`.
Parameters in its `__init__()` method are configured as
FastAPI dependencies,
and other methods of that class instance perform the logic:

```py
class AuthorService:
    def __init__(self, async_session_maker: AsyncSessionMakerDep):
        self.async_session_maker = async_session_maker

    async def get_things(self):
        async with self.async_session_maker() as session:
            ...
```

The class is then wrapped in an `Depends` call (and `typing.Annotated`),
creating an injectable dependency of the service itself:

```py
AuthorServiceDep = Annotated[AuthorService, Depends(AuthorService)]
```

> [!NOTE]
> As a general rule, all FastAPI dependency objects in this app
> use the `Dep` suffix to distinguish them.

Finally, in a path operation, we can call on the service dependency:

```py
from fastapi import APIRouter
from .service import AuthorServiceDep

router = APIRouter()

@router.get("/")
async def get_things(author_service: AuthorServiceDep):
    results = await author_service.get_things()
    return {"items": results}
```

- FastAPI's dependency injection system will instantiate
  `AuthorService` and pass that instance to the path function's `author_service`.
- In turn, the `AuthorService`'s sub-dependency, `AsyncSessionMakerDep`,
  is resolved and creates a new `AsyncSessionMaker`,
  passing *that* instance to the
  `async_session_maker` parameter of the class's `__init__`.

This recursive resolution of dependencies allows us to separate
the needs of the *router*
(which only requires the service class so it can call a method there)
and those of the *service*
(which needs to speak to different data sources and caches,
create background tasks, and so on).

The `router.py` code ends up relatively clean,
looking more like a routing table and less like a mash-up of procedural code. And `service.py`, with most methods designated in a class definition,
can better organize its logic with internal methods, helpers, shared methods, etc.

Further, one service can easily call on another directly
to request details from a different module,
without reinventing logic and without needing to make internal API calls (which would be... odd).

### `deps/settings.py` + `deps/db.py`

These two form the dependency chain underneath every service:

- `get_settings()` generates a singleton `Settings` object,
  which reads environment variables to construct all the app settings.
  All of its env vars share a prefix, `TESTTHING__`,
  and even nested details (like those in the `DBSettings` sub-model)
  can be filled in using delimeter `__` between attribute names.

  This is made available as the dependency object `SettingsDep`.

- `get_async_session_maker()` depends on `SettingsDep`,
  and generates a singleton `async_sessionmaker` for use in creating
  database sessions.

  This is made available as the dependency object `AsyncSessionMakerDep`.

> [!NOTE]
> A note on database sessions
> A common pitfall that [FastAPI's docs sadly encourage](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/?h=depende#a-database-dependency-with-yield)
> is to open a database session inside a dependency method,
> `yield` that session,
> and then `.close()` that session in a `finally` block.
> This appears workable from the outside,
> but in some scenarios can lead to dangling connections,
> since FastAPI will choose when to yield back to those dependency methods
> *after the response has been sent*.
>
> I find it better to inject the *sessionmaker*, instead.
> The router and/or service then have explicit control on where the session starts and ends,
> and can more easily close and re-open sessions in the same route for different purposes.

Services will mark `AsyncSessionMakerDep` as a dependency,
then open the session as needed in one of their methods:

```py
class AuthorService:
    def __init__(self, async_session_maker: AsyncSessionMakerDep):
        self.async_session_maker = async_session_maker

    async def get_things(self):
        async with self.async_session_maker() as session:
            results = await session.execute("...")

        # Exiting the block closes the session.
        # Transactions commit or rollback as needed,
        # and we've already freed up the connection
        # for other routes and services to use.

        parsed = [do_something(x) for x in results]
```

Note the `AsyncSessionMakerDep` requires a `SettingsDep` dependency,
but the service doesn't mention it,
because the service **doesn't need to know that**.
At each layer, concerns are separated based on needs of *that* layer,
not on what needs to be wired from one layer to another.

### Testing implications

The dependency injection structure makes testing simpler for individual layers:

- **Router tests** (`test/routers/*/router_test.py`) use a `TestClient`
  against a real `FastAPI` app, but override the service dependency
  (`app.dependency_overrides[AuthorService] = lambda: mock_author_service`,
  via `create_autospec`). This tests routing, status codes, and response
  shaping without ever touching settings or a database.
- **Service tests** (`test/routers/*/service_test.py`) instantiate the real
  service class, wired to a mocked `session_maker`/`AsyncSession`
  (see `mock_session` / `mock_session_maker` in `test/conftest.py`). This
  tests the actual query/commit logic without a real database connection.
- **Deps tests** (`test/deps/`) cover the settings/session-maker dependency needs
  to ensure they work indepedently.

Because each layer only depends on the layer directly below it through `Depends()`,
every layer can be substituted at the boundaries of the others to permit isolated testing,
with no database connections and fewer cases of clever mocks being used.

[fastapi]: https://fastapi.tiangolo.com/
[gh]: https://cli.github.com/
[homebrew]: https://brew.sh/
[just]: https://just.systems/man/en/
[oracle autonomous database]: https://www.oracle.com/autonomous-database/
[pre-commit]: https://pre-commit.com/
[uv]: https://docs.astral.sh/uv/
