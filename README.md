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

See `AGENTS.md` for how different agents (roles) should collaborate on this codebase.

