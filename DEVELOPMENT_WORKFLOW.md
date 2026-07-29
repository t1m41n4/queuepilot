# QueuePilot Development Workflow

QueuePilot is developed through a milestone-based workflow. Each milestone is implemented, validated, reviewed, and accepted before the next milestone begins.

## Workflow

```text
Roadmap
  ↓
Architecture Audit
  ↓
Implementation Plan
  ↓
Milestone Implementation
  ↓
Validation
  ↓
Milestone Review
  ↓
Repeat until phase completion
  ↓
Phase Acceptance Review
  ↓
Architecture Freeze
  ↓
Merge into develop
  ↓
Create Git tag
```

### Roadmap

Define the product and engineering outcomes for the phase. The Technical Roadmap and Business Intelligence Roadmap establish the intended direction and boundaries.

### Architecture Audit

Inspect the current implementation before making changes. Confirm that the proposed work fits the Next.js → FastAPI → Queue Engine → PostgreSQL architecture and does not duplicate existing responsibilities.

### Implementation Plan

State the milestone objective, affected files, assumptions, validation criteria, and explicit out-of-scope work before editing code.

### Milestone Implementation

Implement only the approved milestone scope. Prefer incremental changes and reuse existing services, schemas, and configuration.

### Validation

Run proportionate automated tests, type checks, builds, migrations, Docker checks, API checks, and runtime checks. Record failures and correct them before review.

### Milestone Review

Review the completed milestone critically against its requirements, architecture, product behavior, security posture, and technical debt. A passing build alone is not acceptance.

### Repeat until phase completion

Continue the audit → plan → implementation → validation → review cycle for each milestone in the phase.

### Phase Acceptance Review

Review the entire phase as a cohesive increment. Confirm that all milestones are complete, regressions are absent, and the result supports the roadmap objectives.

### Architecture Freeze

Freeze the accepted architecture and public contracts for the phase. Any later change must be intentional, documented, and reviewed against the frozen baseline.

### Merge into develop

Merge the accepted phase into `develop` only after the acceptance review and architecture freeze are complete.

### Create Git tag

Create a version tag representing the accepted phase baseline, such as `v0.1.0` for Phase 1 and `v0.2.0` for Phase 2.

## Engineering Principles

- The Queue Engine remains the operational source of truth for queue state, ordering, transitions, readiness, position, and ETA.
- Business logic belongs in backend services; route handlers should validate, delegate, and serialize responses.
- The frontend must not calculate queue state, ETA, position, readiness, or valid transitions.
- API contracts remain stable unless an intentional contract change is explicitly approved and documented.
- Architecture is validated before every merge.
- Every milestone includes automated testing and runtime validation appropriate to its risk.
- Every phase ends with an Architecture Freeze before merging into `develop`.
- Security, deployment, observability, and recovery concerns are reviewed as part of delivery rather than deferred until release.
- Work outside the current milestone remains explicitly deferred; later roadmap phases are not implemented early.
