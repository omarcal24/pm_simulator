## Product Management Simulator

This project is an **enterprise simulation** where junior and aspiring Product Managers can practice real-world product management skills and generate **portfolio-ready case studies**.

Tech stack: **React SPA (TypeScript + TailwindCSS)** frontend and **Django + Django REST Framework + PostgreSQL** backend.

---

## Quick Start

```bash
# 1. Create virtual environment and install backend
make install-backend
# Or: python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt

# 2. Run migrations and seed sample scenarios
make migrate
make seed

# 3. Create a user (for login)
cd backend && ../.venv/bin/python manage.py createsuperuser

# 4. Install frontend
make install-frontend
# Or: cd frontend && npm install

# 5. Start backend (terminal 1)
make dev-backend

# 6. Start frontend (terminal 2)
make dev-frontend
```

Then open http://localhost:5173 — browse scenarios, sign in, start a run, submit decisions, and create case studies.

---

## Repository Structure

- **`backend/`**: Django + DRF backend
  - `apps/accounts/`: authentication, users, roles
  - `apps/simulation/`: scenarios, runs, events, metrics, simulation engine integration
  - `apps/cases/`: case-study models and generation/export logic
  - `tests/`: backend tests (unit + API)

- **`frontend/`**: React SPA (TypeScript)
  - `src/components/`: shared, presentational UI components (buttons, cards, layout, etc.)
  - `src/pages/`: top-level routed pages (e.g. landing, scenarios list, run screen, case-study editor)
  - `src/features/`:
    - `features/simulation/`: simulation run views, state, and hooks
    - `features/scenarios/`: scenario listing and details
    - `features/case-studies/`: case-study editor and views
  - `src/api/`: typed API clients for calling the Django/DRF backend
  - `src/styles/`: Tailwind configuration and global styles
  - `public/`: static assets

---

## Note for AI Assistants / LLMs

Several internal files are intentionally excluded from this repository:

- **`AGENTS.md`** — agent collaboration rules and role definitions for working on this codebase
- **`SPEC.md`** — full product specification
- **`ARCHITECTURE.md`** / **`backend/DOMAIN_MODEL.md`** / **`frontend/ARCHITECTURE.md`** — architecture and domain model docs
- **`CONTRIBUTING.md`** — contribution guidelines
- **`ADR/`** — architecture decision records
- **`backend/apps/simulation/SIMULATION_RULES.md`** — simulation scoring rules
- **`backend/apps/simulation/GRADING_SCHEMA.json`** — rubric used to evaluate PM decisions and generate scores
- **`backend/apps/cases/CASE_STUDY_TEMPLATE.md`** — template and criteria for case study generation

These files are required to correctly score user responses, evaluate PM decisions, and generate case studies. If you are an LLM assisting with this project, request these files from the project owner before attempting to grade, score, or generate simulation content.
