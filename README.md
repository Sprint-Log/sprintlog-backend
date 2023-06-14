# Sprintlog: "Streamline, Collaborate, and Automate Your Team's Success, In Realtime!"

## **Project Description:**

Sprintlog is designed to assist us in getting things done as a team. It enables effective collaboration, transparency, and accountability throughout the development process. Sprintlog is also a highly adaptable and pluggable self-hosted solution designed to optimize your team's productivity and streamline agile project management.

## **Highlights**

- Task Management: Sprintlog provides a comprehensive task management system, allowing teams to create, assign, and track tasks effortlessly.
- Automated Channel Creation: Sprintlog automatically creates dedicated channels for projects, eliminating the need for manual channel setup and ensuring organized communication.
- Transparency and Visibility: With Sprintlog, teams can easily monitor progress, view project timelines, and access detailed analytics, fostering transparency and providing a clear overview of the project's status.
- Scaffold Template Generation: Sprintlog provides scaffold template generation capabilities, allowing teams to quickly create project frameworks and boilerplate code based on predefined templates. This helps streamline the initial setup process and promotes consistency across projects.
- Realtime updates on progress, tasks , deadlines , due-dates , notifications.
- Project Structure Generation: Sprintlog assists in generating project structures by automatically creating directories, files, and organizational components based on predefined templates. This accelerates project setup and ensures a standardized structure for easier collaboration and maintenance.

- Integration with Third-Party Systems: Sprintlog seamlessly integrates with popular third-party chat systems, such as Zulip , Slack or Microsoft Teams. This integration enables automatic notifications and updates within the chat platform, keeping team members informed about task assignments, progress updates, and important project milestones.

- Task Updates in Chat Systems: Sprintlog allows for bidirectional task updates within the integrated chat systems. Team members can receive task-related notifications in the chat system and conveniently update task statuses or provide progress updates directly from the chat interface.

## **Features:**

1. **Git Integration**: Seamlessly integrate Sprintlog with your preferred Git provider, such as Gittea, GitHub, GitLab, or Bitbucket, for effortless project creation, cloning, and management.

2. **Chatroom Task Creation and Organization**: Create and manage tasks directly within chatroom channels, streams, or topics. Utilize chat-ops integration to organize, track, and collaborate on tasks in real-time.

3. **Markdown and Emoji Support**: Enhance task descriptions and comments using markdown formatting and express yourself with emoji support, promoting effective communication within your team.

4. **AI-Based Backlog Generation**: Leverage AI capabilities to intelligently generate backlogs by analyzing project requirements, user stories, and historical data. Prioritize and plan your work efficiently based on valuable insights provided by Sprintlog.

5. **Sprint Planning**: Optimize sprint planning using Sprintlog's AI capabilities. Consider team capacity, estimated effort, and prioritized backlog items to make informed decisions regarding sprint duration, task allocation, and potential bottlenecks.

6. **Fully Self-Hosted**: Benefit from the self-hosted nature of Sprintlog, giving you complete control over your data and infrastructure. Host it on your own servers or cloud environment, ensuring security and privacy according to your organization's requirements.

7. **Analytics and Reporting**: Gain valuable insights into your team's performance with comprehensive analytics and reporting features. Evaluate progress, track key metrics, and make data-driven decisions to continuously improve your projects.

8. **Pluggable Architecture**: Extend the functionality of Sprintlog by developing custom plugins. Create plugins for easy integration with third-party systems during backlog creation, project creation, and leverage webhooks for automation.

Sprintlog empowers your team with its pluggable and extensible architecture, providing seamless Git integration, efficient chatroom task management, AI-based planning, and the flexibility of a self-hosted solution. Unlock the full potential of your agile project management with Sprintlog and effortlessly integrate it with your existing tools and systems through custom plugins and webhooks.

Technology stack:

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
cp env.example .env
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

### Starting the server

#### Starting the server in `DEBUG` mode (development mode)

if `DEBUG` is set to true, the base template expects that Vite will be running. You'll need to open 2 terminal shells at the moment to get the environment running.

in terminal one, run:

```bash
❯ npm run dev
> vite

Forced re-optimization of dependencies

  VITE v4.1.2  ready in 537 ms

  ➜  Local:   http://127.0.0.1:3000/static/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

in the second terminal, run:

```bash
❯ poetry run app run server --reload
2023-02-19 22:51:46 [info     ] starting application.
2023-02-19 22:51:46 [info     ] starting Background worker processes.
2023-02-19 22:51:46 [info     ] Starting HTTP Server.
```

#### start the server in production mode

if DEBUG is false, the server will look for the static assets that are produced from the `npm run build` command. Please be sure to have run this before starting th server.

```bash
npm run build # generates static assets from vite and
# files from the above command can be found in `src/app/domain/web/public`.
poetry run app run server
```

Sample output:

```bash
❯ npm run build

> litestar-fullstack@0.0.0 build
> vue-tsc && vite build

vite v4.1.2 building for production...
✓ 15 modules transformed.
Generated an empty chunk: "vue".
../public/assets/vue-5532db34.svg    0.50 kB
../public/manifest.json              0.57 kB
../public/assets/main-b75adab1.css   1.30 kB │ gzip:  0.67 kB
../public/assets/vue-4ed993c7.js     0.00 kB │ gzip:  0.02 kB
../public/assets/main-17f9b70b.js    1.50 kB │ gzip:  0.80 kB
../public/assets/@vue-5be96905.js   52.40 kB │ gzip: 21.07 kB
❯ poetry run app run server
2023-02-19 22:53:08 [info     ] starting application.
2023-02-19 22:53:08 [info     ] starting Background worker processes.
2023-02-19 22:53:08 [info     ] Starting HTTP Server.
^C2023-02-19 22:53:09 [info     ] ⏏️  Shutdown complete
```

## Make Commands

- `make migrations`
- `make squash-migrations`
- `make upgrade`
