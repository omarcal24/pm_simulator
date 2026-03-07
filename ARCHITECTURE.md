# Architecture

This document is the **source of truth** for where things live, how data flows, and the boundaries that keep the codebase maintainable.

> Project: **Product Management Simulator** — an enterprise simulation where aspiring/junior PMs practice real-world PM skills and generate portfolio-ready case studies.

## Tech stack

- **Frontend:** React SPA (TypeScript, React Router, TailwindCSS)
- **Backend:** Django + Django REST Framework + PostgreSQL
- Optional: Celery + Redis for async tasks (case-study export, long simulations, batch scoring)

## Repository map

- `backend/apps/accounts/` — authentication, user profiles, org/workspace (if/when needed)
- `backend/apps/simulation/` — scenarios, runs, decisions, events, metrics, simulation engine integration
- `backend/apps/cases/` — case study drafts, templates, exports (markdown/pdf), sharing
- `frontend/src/api/` — typed API client wrappers (no raw fetch in pages)
- `frontend/src/features/` — feature modules (scenarios, run UI, case studies)
- `frontend/src/components/` — shared UI building blocks

## Core domain flow

**Scenario → Run → Decision (Step) → Event(s) + Metric snapshot → Debrief → Case Study**

1. A user selects a **Scenario** (with learning objectives + constraints).
2. The backend creates a **Run** (a user’s instance of the scenario).
3. The user submits a **Decision** for the current step/turn.
4. The simulation engine produces:
   - **Events** (stakeholder reactions, incidents, discoveries)
   - **MetricSnapshots** (KPI time series updates)
   - Updated **RunState** (next step prompt / new constraints)
5. A **Debrief** summarizes tradeoffs and learning points.
6. A **CaseStudy** is created/updated using the run history and template.

## Responsibilities and boundaries

### Backend boundaries

**Rule 1 — engine purity:** core simulation logic must be in pure Python modules (no Django imports inside the engine).  
**Rule 2 — DRF is glue:** viewsets/serializers should validate IO and call the engine; they should not contain business logic.  
**Rule 3 — persistence at edges:** database writes happen in service functions around engine calls, not inside the engine.

Recommended layout inside `backend/apps/simulation/`:

- `engine/` — pure Python simulation engine
- `services/` — orchestrates DB + engine + transactions
- `api/` — DRF viewsets/serializers/routers
- `models.py` — Django models for scenarios/runs/decisions/events/metrics

### Frontend boundaries

- `src/api/` is the only place allowed to know URLs and HTTP details.
- `src/features/<feature>/` owns its pages, local components, and hooks.
- `src/components/` contains only reusable, generic UI pieces.

## Run state machine

A run should be represented as a simple state machine.

Suggested statuses:

- `draft` — created but not started (rare; optional)
- `active` — accepting decisions
- `paused` — temporarily not accepting decisions
- `completed` — final debrief generated
- `abandoned` — user ended early

Invariants:

- decisions can only be created when `status == active`
- engine step number must be monotonic (no skipping without a recorded system event)
- every decision produces **at least one** MetricSnapshot (even if unchanged)

## Data ownership rules

- `simulation` app owns: **Scenario**, **Run**, **Decision**, **Event**, **MetricSnapshot**
- `cases` app owns: **CaseStudy**, **CaseStudySection**, **ExportJob**
- `accounts` app owns: **User**, optional **Workspace/Org**, permissions

No circular ownership:
- `cases` may reference `Run` and `Scenario` by FK, but run history stays in `simulation`.

## API conventions

- JSON-only APIs, versioned under `/api/v1/`
- Consistent envelope for errors:
  - `{ "detail": "...", "code": "...", "fields": { ... } }`
- Prefer REST resources + a small number of **actions**:
  - `/runs/{id}/decisions/` (create decision)
  - `/runs/{id}/history/` (read-only)
  - `/runs/{id}/debrief/` (generated summary)
  - `/runs/{id}/case-study/` (create/update case study artifacts)

## Suggested frontend routes

- `/` — overview
- `/scenarios` — list
- `/scenarios/:id` — detail + learning objectives
- `/runs/:id` — main simulation UI
- `/case-studies/:id` — editor/export

## Testing strategy

### Backend
- Engine unit tests: deterministic, pure functions
- Service tests: DB + transactions
- API tests: critical endpoints and permissions

### Frontend
- Smoke tests for routes
- Component tests for run UI + case study editor
- Contract tests for API wrappers (mock server)

## Logging & observability

- Log decision submissions and engine outcomes (step number, seed, event counts)
- Keep a stable **replay key** (seed + scenario version) for debugging

## Future-proofing

- Scenario versions: scenarios must be versioned so old runs remain replayable
- Determinism: prefer seeded randomness for reproducibility
- Export pipeline: generate exports asynchronously when possible