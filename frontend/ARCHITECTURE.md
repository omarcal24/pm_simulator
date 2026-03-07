# Frontend Architecture

This document defines conventions for the React SPA.

## Folder responsibilities

- `src/pages/` — route-level pages (wire features together)
- `src/features/` — domain features:
  - `scenarios/` (list + detail)
  - `frontend/` (shared app shell, routing helpers)
  - `case-studies/` (editor, export, sharing)
- `src/components/` — shared UI components (Button, Card, Modal, Tabs, etc.)
- `src/api/` — API clients and types
- `src/styles/` — global styles, Tailwind config references

## API layer

Rules:
- Pages and components should call **feature hooks**, not raw HTTP.
- `src/api/` owns:
  - base client (fetch wrapper)
  - endpoint functions (e.g., `listScenarios()`)
  - shared types/interfaces

## State management

- Prefer local state + React Query (if adopted) for server state.
- Keep feature-level state inside `src/features/<feature>/hooks`.
- Avoid global state unless a clear cross-cutting need exists.

## Route map (suggested)

- `/scenarios`
- `/scenarios/:id`
- `/runs/:id`
- `/case-studies/:id`

## UX principles for the simulator

- Always show:
  - current goal
  - constraints
  - current KPI panel (with deltas)
  - timeline of decisions/events
- Keep decisions structured:
  - selectable options + required rationale
  - expandable “why this matters” learning hints