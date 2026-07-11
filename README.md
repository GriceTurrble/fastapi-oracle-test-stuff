# fastapi-oracle-test-stuff

An example [FastAPI] application backed by a free [Oracle Autonomous Database],
used to try out the connection and libraries for talking to Oracle from Python.

## Development setup

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

[fastapi]: https://fastapi.tiangolo.com/
[gh]: https://cli.github.com/
[homebrew]: https://brew.sh/
[just]: https://just.systems/man/en/
[oracle autonomous database]: https://www.oracle.com/autonomous-database/
[pre-commit]: https://pre-commit.com/
[uv]: https://docs.astral.sh/uv/
