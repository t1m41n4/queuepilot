# QueuePilot

QueuePilot is a web-based smart queue management system for bank branches. Customers can find a participating branch, join its queue remotely, follow live status, and cancel when plans change. Staff use a branch-scoped dashboard to operate queues, while the deterministic Queue Engine remains the authoritative source of queue state.

## Problem statement

Bank customers often spend significant time waiting in crowded branches, while staff lack a shared, real-time view of queue demand and service progress. QueuePilot addresses both sides with remote queue joining, transparent status updates, branch-aware operations, and a read-only assistant that explains queue conditions.

## Solution overview

The application separates presentation, persistence, and queue decisions:

- The Next.js frontend presents customer and staff workflows and consumes backend responses.
- FastAPI exposes REST and WebSocket interfaces.
- The Queue Engine owns queue transitions, ordering, readiness, position, and ETA decisions.
- PostgreSQL stores banks, branches, queues, entries, events, and staff accounts.
- The Queue Operations Assistant explains live Queue Engine data without modifying queue state.

## Key features

- Customer bank and branch selection, remote queue joining, live status, and cancellation.
- Deterministic queue processing for waiting, ready, checked-in, serving, completed, cancelled, and skipped states.
- Branch recommendations based on open-queue operational data.
- Staff login with JWT bearer authentication and Argon2 password hashing.
- Branch-scoped staff dashboard with queue summaries and operations.
- Native WebSocket updates for supported queue events.
- Read-only Queue Operations Assistant powered by the OpenAI Chat Completions API.
- Swagger/OpenAPI documentation for the backend API.

## Technology stack

- **Frontend:** Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui-style components
- **Backend:** FastAPI, Pydantic, SQLAlchemy 2.x, Alembic
- **Database:** PostgreSQL
- **Authentication:** JWT (PyJWT), Argon2 password hashing via pwdlib
- **Realtime:** FastAPI native WebSockets
- **AI:** OpenAI Chat Completions API
- **Infrastructure:** Docker and Docker Compose

## Project architecture

\`\`\`text
Browser (Next.js)
        │ REST + WebSocket
        ▼
FastAPI API layer ─── Authentication / schemas
        │
        ├── Queue Engine (authoritative queue decisions)
        ├── Assistant service (read-only explanations)
        ├── Realtime publisher / connection manager
        └── SQLAlchemy services and models
                         │
                         ▼
                    PostgreSQL
\`\`\`

The frontend does not calculate queue position, ETA, readiness, or valid queue transitions. Those values are returned by the backend.

## Repository structure

\`\`\`text
queuepilot/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/v1/           # Versioned REST routers
│   │   ├── core/             # Configuration and security
│   │   ├── db/               # Sessions, metadata, and seed data
│   │   ├── models/           # SQLAlchemy persistence models
│   │   ├── realtime/         # WebSocket manager and publishers
│   │   ├── schemas/          # Pydantic contracts
│   │   └── services/         # Queue Engine and application services
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                  # App Router pages
│   ├── components/           # Reusable presentation components
│   ├── lib/                  # API client and TypeScript contracts
│   └── Dockerfile
├── docs/
├── docker-compose.yml
└── README.md
\`\`\`

## Prerequisites

For the recommended setup:

- Docker Desktop with Docker Compose

For running without Docker:

- Python 3.13 or a compatible Python 3.x environment
- Node.js 22 or newer and npm
- PostgreSQL 16 or a compatible PostgreSQL installation

## Environment configuration

Three environment-file scopes are used:

- Root `.env`: Docker Compose interpolation for PostgreSQL credentials, exposed ports, JWT settings, and OpenAI settings. Start from the root `.env.example` when customizing Compose.
- `backend/.env`: settings read by FastAPI or Alembic directly without Docker. Start from `backend/.env.example`.
- `frontend/.env.local`: Next.js browser configuration for non-Docker development. Start from `frontend/.env.example`.

These files are separate because Docker Compose and local application processes load configuration from different locations. Never commit real secrets.

Important backend settings:

| Variable | Purpose | Example |
| --- | --- | --- |
| \`DATABASE_URL\` | PostgreSQL connection | \`postgresql+psycopg://queuepilot:queuepilot@localhost:5432/queuepilot\` |
| \`JWT_SECRET_KEY\` | JWT signing secret | \`change-me-in-production\` |
| \`JWT_ALGORITHM\` | JWT algorithm | \`HS256\` |
| \`JWT_ACCESS_TOKEN_EXPIRE_MINUTES\` | Access-token lifetime | \`30\` |
| \`OPENAI_API_KEY\` | Assistant API key | *(required for live answers)* |
| \`OPENAI_MODEL\` | OpenAI model | \`gpt-4o-mini\` |
| \`ENVIRONMENT\` | Runtime environment; production rejects weak JWT secrets | \`development\` |
| \`CORS_ALLOWED_ORIGINS\` | Comma-separated browser origins | \`http://localhost:3000,http://127.0.0.1:3000\` |
| \`MIGRATION_MAX_RETRIES\` | Maximum transient migration attempts at startup | \`10\` |
| \`MIGRATION_RETRY_DELAY_SECONDS\` | Delay between migration attempts | \`3\` |

The frontend uses:

\`\`\`text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
\`\`\`

Do not commit real secrets.

## Local setup

### Backend

From \`backend/\`:

\`\`\`powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
\`\`\`

With PostgreSQL running and \`DATABASE_URL\` configured:

\`\`\`powershell
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

Application startup seeds deterministic demo data when the database is available.

### Frontend

From \`frontend/\`:

\`\`\`powershell
npm ci
npm run dev
\`\`\`

Open http://localhost:3000.

## Running the application with Docker Compose

From the repository root, create the root `.env` from `.env.example` if you need to customize Compose values, then run:

\`\`\`powershell
docker compose up -d --build
\`\`\`

The backend image runs `alembic upgrade head` automatically before starting Uvicorn. It retries transient migration failures using `MIGRATION_MAX_RETRIES` and `MIGRATION_RETRY_DELAY_SECONDS`. Compose waits for PostgreSQL readiness, then the backend readiness check, before starting the frontend. On a clean clone, Compose creates the database schema and then runs the normal application startup and seed logic without a manual migration step.

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Check status:

\`\`\`powershell
docker compose ps
\`\`\`

The repository also contains a basic CI workflow at `.github/workflows/ci.yml`. It runs backend tests, the frontend production build, and Compose configuration validation on pushes and pull requests.

All three services should report `Up`; PostgreSQL should report `healthy`, and backend/frontend should report `healthy` after their startup grace period. Inspect startup diagnostics with `docker compose logs --tail=100 backend`.

Stop the stack:

\`\`\`powershell
docker compose down
\`\`\`

PostgreSQL data is stored in the `postgres_data` volume. Use `docker compose down -v` only when intentionally removing persisted data; removing the volume causes migrations and seed data to run again on the next startup.

The frontend public API URL is passed to the Next.js production build through `NEXT_PUBLIC_API_BASE_URL` in the root `.env`. Change it before `docker compose up -d --build` when the browser must reach a non-local backend.

## Running the application without Docker

Running without Docker is supported when PostgreSQL is installed locally. Start PostgreSQL, configure \`backend/.env\`, apply migrations, then start the backend and frontend using the commands above.

## Database migrations

Alembic is configured in \`backend/alembic.ini\` and uses the registered SQLAlchemy metadata.

\`\`\`powershell
cd backend
alembic upgrade head
\`\`\`

With Compose, migrations run automatically in the backend entrypoint before Uvicorn starts. To re-run or inspect them manually after the stack is running:

\`\`\`powershell
docker compose exec backend alembic upgrade head
\`\`\`

If migrations fail, the backend exits after the configured retry limit and Compose marks it unhealthy. Fix the configuration or database state, then restart with `docker compose up -d backend`.

## Backup, restore, and rollback

Create a logical PostgreSQL backup while the stack is running:

\`\`\`powershell
.\\scripts\\backup-db.ps1
\`\`\`

This writes a timestamped SQL dump under `backups/`. Store backups outside the repository and protect them as sensitive data.

Restore a dump only during a planned recovery window. Restore replaces database objects contained in the dump:

\`\`\`powershell
.\\scripts\\restore-db.ps1 -BackupFile .\\backups\\queuepilot-YYYYMMDD-HHMMSS.sql -ConfirmRestore
docker compose restart backend frontend
\`\`\`

For an application rollback, check out the last known-good commit or image tag and run `docker compose up -d --build`. Preserve the PostgreSQL volume. Do not run `docker compose down -v` during an application rollback because that permanently removes the database volume. Database migrations are forward-only in this MVP; restore a compatible backup before rolling back across an incompatible schema change.

## Clean-clone deployment checklist

1. Install Docker Desktop with Compose support.
2. Clone the repository and enter its directory.
3. Copy `.env.example` to `.env` and replace production secrets, especially `JWT_SECRET_KEY`.
4. Run `docker compose up -d --build`.
5. Run `docker compose ps` and wait for healthy backend/frontend status.
6. Verify `http://localhost:8000/api/v1/health`, `/api/v1/health/live`, `/api/v1/health/ready`, and `http://localhost:3000`.
7. Open Swagger at `http://localhost:8000/docs` and use the documented demo account for a pilot check.

No manual Alembic command is required for a clean Docker deployment.

The initial migration creates the MVP persistence tables. Application startup seeds demo records; it does not replace migration management.

## Seed/demo accounts and sample data

Startup seeding creates or preserves:

- QueuePilot Demo Bank
- QueuePilot CBD with an OPEN queue by default
- QueuePilot Westlands with an OPEN queue by default
- CBD staff:
  - Email: \`staff@queuepilot.local\`
  - Password: \`password123\`
- Westlands staff:
  - Email: \`staff.westlands@queuepilot.local\`
  - Password: \`password123\`

Passwords are stored as hashes. Change demo credentials and JWT secrets for any non-demo deployment.

## Available API documentation

Interactive Swagger documentation:

http://localhost:8000/docs

Raw OpenAPI:

http://localhost:8000/openapi.json

The API is versioned under \`/api/v1\`. Endpoint groups include:

- Health: \`GET /api/v1/health\`, \`GET /api/v1/health/live\`, \`GET /api/v1/health/ready\`
- Metrics: \`GET /api/v1/metrics\`
- Banks and branches
- Customer queue join, status, and cancellation
- Staff login, dashboard, queue operations, pause, and resume
- Assistant: \`POST /api/v1/assistant/chat\`
- WebSocket: \`/ws/queue/{branch_id}\`

## Application walkthrough

### Customer flow

1. Open the landing page and choose **Find a branch**.
2. Select a participating bank.
3. Select a branch. The page displays backend-provided estimated wait and recommendation status.
4. Enter a customer name and join the queue.
5. View queue number, branch, position, ETA, and status.
6. Receive supported live queue updates through WebSockets.
7. Cancel the queue entry when needed.
8. Ask the read-only Queue Operations Assistant about the current queue.

### Staff flow

1. Open **Staff portal** and sign in with a seeded account.
2. The dashboard is scoped to the authenticated staff member’s assigned branch.
3. Review queue status, waiting/ready/checked-in counts, current customer, and active entries.
4. Use backend-provided actions such as Check In, Call Next, and Complete Service.
5. Pause or resume the queue.
6. Dashboard data refreshes from backend responses and supported WebSocket events.

## Testing and verification

Useful checks:

\`\`\`powershell
Invoke-RestMethod http://localhost:8000/api/v1/health

cd frontend
npm run build

cd ..
docker compose ps
\`\`\`

The project has been verified through the milestone workflow with API, authentication, queue transition, WebSocket, Swagger, frontend build, and Docker Compose checks. Invalid queue transitions are intentionally rejected by the Queue Engine.

## Known limitations

- Staff accounts are assigned to one branch at a time.
- The Queue Operations Assistant requires a valid \`OPENAI_API_KEY\`; without one, it fails gracefully.
- WebSocket connections are maintained in the backend process and target the current single-process MVP deployment.
- Customer authentication and authorization are not implemented.
- The frontend does not use polling or calculate queue state.

## Future improvements

Potential follow-on work includes customer identity/authentication, production-grade multi-instance realtime infrastructure, richer staff administration, automated tests, observability, deployment hardening, and expanded queue analytics.

## AI-Assisted Development

GPT-5.6 was used throughout the project for architecture discussions, implementation planning, milestone definition, reviewing design decisions, debugging guidance, prompt engineering, and code review assistance.

Codex was used as the primary AI coding assistant to implement the project milestone by milestone, generate code, apply targeted fixes, and perform implementation verification.

Development followed a milestone-based workflow where each milestone was implemented, verified, committed, and stabilized before moving to the next.

All architectural decisions, business rules, and Queue Engine behavior were reviewed by the developer before acceptance.

The developer remained responsible for validating functionality, testing the application, reviewing generated code, and making final implementation decisions.

## License

No license has been selected yet. Until a license is added to the repository, all rights are reserved by the project owner.
