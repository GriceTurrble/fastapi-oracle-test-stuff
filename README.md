# python-project-template

Basic template for a Python project

## Using this template

- Click the [Use this template] button to create a new repo for this project.

  After the new repo is created, clone it locally as needed.

- Edit [`.gitignore`](.gitignore), removing the following lines (near the bottom):

  ```gitignore
  # Remove the ignore on uv.lock after generating project!
  uv.lock
  ```

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

> [!NOTE]
> These will generate some initial changes, such as a `uv.lock` file that is excluded from the template.
> Please commit these changes before continuing.

[gh]: https://cli.github.com/
[homebrew]: https://brew.sh/
[just]: https://just.systems/man/en/
[pre-commit]: https://pre-commit.com/
[use this template]: https://github.com/new?template_name=python-project-template&template_owner=GriceTurrble
[uv]: https://docs.astral.sh/uv/
