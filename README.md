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

(Next.js)
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


The frontend does not calculate queue position, ETA, readiness, or valid queue transitions. Those values are returned by the backend.

## Repository structure


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

## Prerequisites

For the recommended setup:

- Docker Desktop with Docker Compose

For running without Docker:

- Python 3.13 or a compatible Python 3.x environment
- Node.js 22 or newer and npm
- PostgreSQL 16 or a compatible PostgreSQL installation


## Running the application with Docker Compose

From the repository root, create the root `.env` from `.env.example` if you need to customize Compose values, then run:

\`\`\`powershell
docker compose up -d --build
\`\`\`

The backend image runs `alembic upgrade head` automatically before starting Uvicorn. On a clean clone, Compose creates the database schema and then runs the normal application startup and seed logic without a manual migration step.

Check status:

\`\`\`powershell
docker compose ps
\`\`\`

Stop the stack:

\`\`\`powershell
docker compose down
\`\`\`

PostgreSQL data is stored in the `postgres_data` volume. Use `docker compose down -v` only when intentionally removing persisted data; removing the volume causes migrations and seed data to run again on the next startup.

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
