# Sprintlog: "Streamline, Collaborate, and Automate Your Team's Success, Live!"

## **Project Description:**

<div align="center">
<!-- prettier-ignore-start -->

| Project   |     | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------- | :-- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CI/CD     |     | [![Tests and Linting](https://github.com/litestar-org/litestar-fullstack/actions/workflows/ci.yaml/badge.svg)](https://github.com/litestar-org/litestar-fullstack/actions/workflows/ci.yaml) [![Documentation Building](https://github.com/litestar-org/litestar-fullstack/actions/workflows/docs.yaml/badge.svg)](https://github.com/litestar-org/litestar-fullstack/actions/workflows/docs.yaml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Quality   |     | [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-fullstack&metric=coverage)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-fullstack&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-fullstack&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar) [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-fullstack&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-fullstack&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar)                                                                                                                                                                                                                     |
| Community |     | [![Reddit](https://img.shields.io/reddit/subreddit-subscribers/litestarapi?label=r%2FLitestar&logo=reddit&labelColor=202235&color=edb641&logoColor=edb641)](https://reddit.com/r/litestarapi) [![Discord](https://img.shields.io/discord/919193495116337154?labelColor=202235&color=edb641&label=chat%20on%20discord&logo=discord&logoColor=edb641)](https://discord.gg/X3FJqy8d2j) [![Matrix](https://img.shields.io/badge/chat%20on%20Matrix-bridged-202235?labelColor=202235&color=edb641&logo=matrix&logoColor=edb641)](https://matrix.to/#/#litestar:matrix.org) [![Medium](https://img.shields.io/badge/Medium-202235?labelColor=202235&color=edb641&logo=medium&logoColor=edb641)](https://blog.litestar.dev) [![Twitter](https://img.shields.io/twitter/follow/LitestarAPI?labelColor=202235&color=edb641&logo=twitter&logoColor=edb641&style=flat)](https://twitter.com/LitestarAPI) [![Blog](https://img.shields.io/badge/Blog-litestar.dev-202235?logo=blogger&labelColor=202235&color=edb641&logoColor=edb641)](https://blog.litestar.dev)                                                                                                                                                                                              |
| Meta      |     | [![Litestar Project](https://img.shields.io/badge/Litestar%20Org-%E2%AD%90%20Litestar-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/litestar-org/litestar) [![types - Mypy](https://img.shields.io/badge/types-Mypy-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://spdx.org/licenses/) [![Litestar Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23edb641.svg?&logo=github&logoColor=edb641&labelColor=202235)](https://github.com/sponsors/litestar-org) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json&labelColor=202235)](https://github.com/astral-sh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&labelColor=202235&logoColor=edb641)](https://github.com/psf/black) [![All Contributors](https://img.shields.io/github/all-contributors/litestar-org/litestar?labelColor=202235&color=edb641&logoColor=edb641)](#contributors-) |

<!-- prettier-ignore-end -->
</div>

# Litestar Fullstack Reference Application

> [!WARNING]\
> This repo is referencing a currently unreleased version of Litestar 2.0. Expect things to stabilize as we get closer to a final release.

Sprintlog is also a highly adaptable and pluggable self-hosted solution designed to optimize your team's productivity and streamline agile project management.

It contains most of the boilerplate required for a production web API with features like:

Language :

- Python , Typescript ,Svelte,Tailwind

Framework

- Litestar (2.0) , Sqlalchemy , Sveltekit, TanStackQuery

Repo:

- <https://git.hexcode.tech/hexcode-core/sprintlog-backend>
- <https://git.hexcode.tech/hexcode-core/sprintlog-frontend>

Preliminary requirements tutorials for development contribution:

Backend:

- <https://docs.litestar.dev/dev/tutorials/todo-app/index.html>
- <https://docs.litestar.dev/dev/usage/dto.html>
- <https://docs.litestar.dev/dev/tutorials/dto-tutorial/index.html>
- <https://docs.litestar.dev/dev/usage/websockets.html>
- <https://docs.litestar.dev/dev/usage/plugins/sqlalchemy.html>

Frontend

- <https://www.skeleton.dev/elements/chat>
- <https://tanstack.com/query/latest/docs/svelte/examples/svelte/auto-refetching>
- <https://flowbite.com/#components>
- Latest Litestar configured with best practices
- Integration with [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [SAQ (Simple Asynchronous Queue)](https://saq-py.readthedocs.io/en/latest/), and [Structlog](https://www.structlog.org/en/stable/)
- Extends built-in Litestar click CLI
- Frontend integrated with ViteJS and includes Jinja2 templates that integrate with Vite websocket/HMR support
- Multi-stage Docker build using a Google Distroless (distroless/cc) Python 3.11 runtime image.
- Pre-configured user model that includes teams and associated team roles
- Examples of using guards for superuser and team-based auth.

## App Commands

```bash
❯ poetry run app

 Usage: app [OPTIONS] COMMAND [ARGS]...

 Litestar Reference Application

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help    Show this message and exit.                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ manage         Application Management Commands                               │
│ run            Run application services.                                     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## Management Commands

```bash
❯ poetry run app manage

 Usage: app manage [OPTIONS] COMMAND [ARGS]...

 Application Management Commands

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help    Show this message and exit.                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ create-database                 Creates an empty postgres database and       │
│                                 executes migrations                          │
│ create-user                     Create a user                                │
│ export-openapi                  Generate an OpenAPI Schema.                  │
│ export-typescript-types         Generate TypeScript specs from the OpenAPI   │
│                                 schema.                                      │
│ generate-random-key             Admin helper to generate random character    │
│                                 string.                                      │
│ promote-to-superuser            Promotes a user to application superuser     │
│ purge-database                  Drops all tables.                            │
│ reset-database                  Executes migrations to apply any outstanding │
│                                 database structures.                         │
│ show-current-database-revision  Shows the current revision for the database. │
│ upgrade                Executes migrations to apply any outstanding │
│                                 database structures.                         │
╰──────────────────────────────────────────────────────────────────────────────╯

```

## Run Commands

```bash
❯ poetry run app run

 Usage: app run [OPTIONS] COMMAND [ARGS]...

 Run application services.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help    Show this message and exit.                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ server          Starts the application server                                │
│ worker          Starts the background workers                                │
╰──────────────────────────────────────────────────────────────────────────────╯

```

```bash
❯ poetry run app run server --help

 Usage: app run server [OPTIONS]

 Starts the application server

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --host                    Host interface to listen on.  Use 0.0.0.0 for all  │
│                           available interfaces.                              │
│                           (TEXT)                                             │
│                           [default: 0.0.0.0]                                 │
│ --port                -p  Port to bind. (INTEGER) [default: 8000]            │
│ --http-workers            The number of HTTP worker processes for handling   │
│                           requests.                                          │
│                           (INTEGER RANGE)                                    │
│                           [default: 7; 1<=x<=7]                              │
│ --worker-concurrency      The number of simultaneous jobs a worker process   │
│                           can execute.                                       │
│                           (INTEGER RANGE)                                    │
│                           [default: 10; x>=1]                                │
│ --reload              -r  Enable reload                                      │
│ --verbose             -v  Enable verbose logging.                            │
│ --debug               -d  Enable debugging.                                  │
│ --help                    Show this message and exit.                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

```bash
❯ poetry run app run worker --help

 Usage: app run worker [OPTIONS]

 Starts the background workers

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --worker-concurrency      The number of simultaneous jobs a worker process   │
│                           can execute.                                       │
│                           (INTEGER RANGE)                                    │
│                           [default: 1; x>=1]                                 │
│ --verbose             -v  Enable verbose logging.                            │
│ --debug               -d  Enable debugging.                                  │
│ --help                    Show this message and exit.                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Installation and Configuration

Commands to help you get this repository running.

### Install virtual environment and node packages

Most of the development related tasks are included in the `Makefile`. To install an environment with all development packages run:

```bash
make install
```

This command does the following:

- install `poetry` if it is not available in the path.
- create a virtual environment with all dependencies configured
- executes `npm ci` to install the node modules into the environment
- run `npm run build` to generate the static assets

### Edit .env configuration

There is a sample `.env` file located in the root of the repository.

```bash
cp .env.example .env
```

**Note** `SECRET_KEY`, `DATABASE_URI`, and `REDIS_URL` are the most important config settings. Be sure to set this properly.

You can generate a `SECRET_KEY` by running:

```bash
❯ poetry run app manage generate-random-key
KEY: 5c5f2230767976c332b6f933b63b483a35148b2218e2cdfd0da992d859feae19
```

### Deploy Database Migrations

You can run most of the database commands with the integrated CLI tool.

To deploy migration to the database, execute:
`poetry run app manage upgrade`

## Make Commands

- `make migrations`
- `make squash-migrations`
- `make upgrade`
