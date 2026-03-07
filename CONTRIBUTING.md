# Contributing

## Principles
- Keep simulation engine pure (no Django imports inside engine modules).
- DRF should be glue (validation + orchestration only).
- Frontend should not call raw endpoints outside `src/api`.

## Repo structure
- `backend/apps/simulation/` — scenarios, runs, engine integration
- `backend/apps/cases/` — case study generation + export
- `backend/apps/accounts/` — auth / user data
- `frontend/src/features/` — feature modules
- `frontend/src/api/` — API client functions + types

## Branching & PRs
- Branches: `feature/<name>`, `fix/<name>`
- PRs must include:
  - what changed
  - why
  - test plan (commands + screenshots if UI)

## Code style
Backend:
- Prefer small service functions
- Keep serializers thin
- Add tests for engine and services

Frontend:
- Put domain logic in feature hooks
- Reusable UI in `src/components`
- No URL strings outside `src/api`

## Adding a new API endpoint
1. Add route/view
2. Add serializer(s)
3. Add service function (if business logic)
4. Add tests
5. Update `backend/API_SPEC.md`

## Adding a new scenario
1. Add scenario config (DB seed or fixture)
2. Add/extend engine support for any new decision type
3. Add engine tests for deterministic outputs
4. Verify run can be completed end-to-end

## Testing (expected)
Backend:
- Unit tests for engine behavior
- API tests for key endpoints

Frontend:
- Smoke test main routes
- Minimal component tests for run + case study editor