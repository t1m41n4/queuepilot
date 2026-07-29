# Changelog

All notable QueuePilot project milestones are documented here. This changelog follows the general structure of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Future work will be recorded here as it is planned and accepted. Phase 3 has not started.

## [0.2.0] — Phase 2: Production Foundation

### Added

- Backend branch isolation and staff authorization enforcement.
- Queue Engine transition validation and PostgreSQL-compatible locking behavior.
- Automated API, authorization, Queue Engine, WebSocket, seed-data, PostgreSQL, and concurrency tests.
- JWT security hardening, Argon2 password verification, login rate limiting, request limits, secure headers, and safe error responses.
- Structured operational logging, request correlation IDs, health/readiness/liveness checks, metrics, and security event telemetry.
- Docker startup retries for migrations, service health checks, deployment diagnostics, backup/restore helpers, rollback guidance, and CI validation.

### Changed

- Docker Compose startup now waits for service health before dependent services start.
- Frontend production builds accept a configurable public backend URL.

## [0.1.0] — Phase 1: MVP Polish

### Added

- Polished customer and staff MVP workflows across responsive Next.js screens.
- Branch availability presentation and recommendation-aware customer navigation.
- Accessible queue-cancellation confirmation and improved staff login navigation.
- Browser-level workflow and accessibility validation for the primary customer and staff journeys.

## Project Origin — Hackathon MVP

QueuePilot originated as an OpenAI Build with Codex Hackathon MVP: a branch queue management platform with a Next.js frontend, FastAPI backend, PostgreSQL persistence, a deterministic Queue Engine, staff operations, realtime updates, and a read-only Queue Operations Assistant.
