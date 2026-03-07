# ADR 0001 — Architecture boundaries

## Status
Accepted

## Context
We need predictable boundaries to avoid business logic leaking across Django views/serializers and to keep the simulation engine testable and deterministic.

## Decision
- Keep the simulation engine pure Python (no Django imports).
- Persist engine IO at the service layer (run state, events, metric snapshots).
- DRF layer validates and delegates.

## Consequences
- Engine can be unit tested without DB.
- API logic stays thin and consistent.
- More explicit service layer, but higher maintainability.