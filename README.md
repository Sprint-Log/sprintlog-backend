# Sprintlog: "Streamline, Collaborate, and Automate Your Team's Success, Live!"

## **Project Description:**

Sprintlog is also a highly adaptable and pluggable self-hosted solution designed to optimize your team's productivity and streamline agile project management.

## **Highlights**

- Task Management: Create, assign, and track tasks easily.
- Automated Channel Creation: Automatically creates channels for projects.
- Visibility: Monitor progress, view project timelines, and access analytics.
- Scaffold Template Generation: Automatically generate project repos and boilerplate code on creation of projects, integrated with gitea.
- Real-time updates on progress, tasks, deadlines, and notifications.
- Project Structure Generation: Automatically create directories, files, and organizational components.
- Integration with Third-Party Systems: Seamlessly integrate with popular chat systems.
- Chat Notificaiton Integartion: Receive task-related notifications and update task statuses from the chat interface. Chatroom creation based on project names and organization
- Git branch and commits integration
- Markdown and emoji support
- AI-based backlog and project specs generation
- Sprint planning
- 100% Self-hostable , including LLMs
- Analytics and reporting
- Pluggable architecture for custom plugins

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
│ upgrade-database                Executes migrations to apply any outstanding │
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
`poetry run app manage upgrade-database`

## Make Commands

- `make migrations`
- `make squash-migrations`
- `make upgrade`
