### AGENTS.md

This document defines how AI agents should collaborate on this project: an **enterprise simulation** where junior and aspiring Product Managers learn core PM principles and generate **portfolio-ready case studies**.

Tech stack: **React SPA (TypeScript + TailwindCSS)** frontend, **Django + Django REST Framework + PostgreSQL** backend.

---

## Project Vision

- **Goal**: Build an interactive, realistic PM simulation where users act as Product Managers, make decisions, and see their impact over time.
- **Primary users**: Junior / aspiring Product Managers.
- **Outcomes**:
  - Practicing core PM skills (discovery, prioritization, roadmap, execution, stakeholder management, metrics).
  - Producing structured **case studies** they can use in interviews and portfolios.

---

## Global Guidelines for All Agents

- **User-first learning**: Every feature must clearly support a PM learning objective, not just add complexity.
- **Stack alignment**:
  - **Frontend**: React SPA (TypeScript, React Router, TailwindCSS).
  - **Backend**: Django, Django REST Framework, PostgreSQL; optional Celery + Redis for async tasks.
- **APIs first**: Any simulation capability should be exposed via a **clean DRF API** before being wired into the React UI.
- **Modularity**:
  - **Frontend**: Small, reusable components and hooks; clear separation of pages vs shared UI.
  - **Backend**: Simulation logic in pure Python modules, kept separate from DRF views/serializers.
- **Documentation**:
  - Update `AGENTS.md` and `README.md` when adding major features, flows, or architectural decisions.
- **Testing**:
  - Frontend: tests for core pages and components (e.g. run screen, metrics charts, case-study editor).
  - Backend: unit tests for simulation engine; API tests for critical endpoints.

---

## Agent Roles

### 1. Product & Curriculum Agent

**Purpose**: Protect the PM learning goals and curriculum.

**Responsibilities**:
- **Define learning objectives** for:
  - The overall product (e.g., “understand end-to-end PM lifecycle”).
  - Each scenario (e.g., “practice prioritization under tight deadlines”).
- Maintain a **scenario catalog**:
  - Scenario name, domain, context, constraints, stakeholders, KPIs, difficulty.
- Define **case study templates**:
  - Standard structure: context, problem, constraints, options, decision, results, reflection.
  - Map which simulation data pre-fills which sections.

**Tech-specific guidelines**:
- Represent scenarios and learning objectives as **Django models** (e.g. `Scenario`, `LearningObjective`) and make them accessible via DRF.
- Ensure the React app surfaces this information clearly on a **Scenario Details** page before a user starts a run.

---

### 2. Simulation Design Agent

**Purpose**: Design how the simulated enterprise behaves and responds to PM decisions.

**Responsibilities**:
- Model key entities:
  - Users, organizations, products, features, stakeholders, experiments, events, metrics, runs.
- Define **decision points** and trade-offs:
  - Prioritization, scope vs. timeline, experiment design, tech debt vs. new features, stakeholder alignment.
- Design **feedback loops**:
  - Immediate metric changes after decisions.
  - Longer-term effects (compounding consequences).

**Tech-specific guidelines**:
- Implement the simulation engine in a dedicated **Python package** (e.g. `simulation/engine/`):
  - Pure, testable functions/classes operating on structured inputs (DTOs or Django model instances).
  - Avoid embedding core logic directly in DRF viewsets.
- Use DRF endpoints for actions such as:
  - **Create run**: start a new simulation run based on a scenario.
  - **Submit decision / step**: apply a decision and return updated state + metrics.
  - **Get run state**: fetch current state, history, metrics timeline.
- Keep scenario parameters and rules **config-driven** where possible (e.g. JSON-like configs stored in DB) to allow new scenarios without deep code changes.

---

### 3. Frontend / UX Agent (React SPA)

**Purpose**: Deliver a clear, motivating, and intuitive UI.

**Responsibilities**:
- Define and maintain **user flows**:
  - Landing → signup/login → scenario selection → run simulation → debrief → case-study creation/export.
- Build main React routes (using React Router), for example:
  - `/` – marketing / overview of what the simulator teaches.
  - `/scenarios` – list of available scenarios.
  - `/scenarios/:id` – scenario details and learning objectives.
  - `/runs/:id` – main simulation UI.
  - `/case-studies/:id` – case-study editor and export page.
- Design UI to:
  - Clearly show current goals, constraints, decisions, and metrics.
  - Emphasize learning via tooltips and short explanations of PM concepts.

**Tech-specific guidelines**:
- Use **TypeScript** for all components and hooks.
- Style with **TailwindCSS**, with a small **design system**:
  - Reusable components: `Button`, `Card`, `Modal`, `Tabs`, `Table`, `MetricBadge`, `ChartPanel`, etc.
- Create a central **API layer** (e.g. `src/api/`) to wrap HTTP calls to Django/DRF:
  - Avoid calling `fetch` or `axios` directly from page components.
- For metrics and timelines, use a charting library (e.g. `recharts`) wrapped in reusable chart components.
- Handle **loading/error states** explicitly and clearly in the UI.

---

### 4. Backend / API Agent (Django + DRF)

**Purpose**: Provide a robust backend, domain model, and clean APIs.

**Responsibilities**:
- Structure the Django project into apps such as:
  - `accounts` – users, roles, authentication.
  - `simulation` – scenarios, runs, events, metrics.
  - `cases` – case study models and exports.
- Implement DRF **viewsets and serializers** for:
  - Scenarios (`/api/scenarios/`).
  - Runs (`/api/runs/` with actions to start, advance, and fetch state).
  - Case studies (`/api/case-studies/` for draft generation, editing, exporting).
- Set up an **authentication** scheme that works smoothly with the React SPA:
  - Either session-based auth (CSR with same-origin) or token/JWT-based auth.

**Tech-specific guidelines**:
- Keep heavy business logic out of views:
  - Use service modules (e.g. `simulation/services.py` or `simulation/engine/`) and call them from viewsets.
- Use **PostgreSQL** features when useful:
  - JSON fields for flexible configurations.
  - Constraints to ensure data integrity (e.g. only one active run per user per scenario, if desired).
- Provide a **Django admin** configuration to inspect scenarios, runs, and case studies during development.

---

### 5. Case Study & Reporting Agent

**Purpose**: Turn simulation histories into high-quality, interview-ready case studies.

**Responsibilities**:
- Define **Django models** for case studies:
  - Link to runs, plus narrative fields (context, problem, constraints, options, decision, results, reflection).
  - Fields for auto-generated content vs. user-edited content.
- Implement **generation logic**:
  - Aggregate run data: key decisions, metric changes, important events.
  - Build a structured draft narrative mapping that data into the case-study template.
- Provide endpoints and UI for:
  - Generating a draft from a completed run.
  - Editing the draft in the browser.
  - Exporting the case study (Markdown, and optionally PDF).

**Tech-specific guidelines**:
- Backend:
  - Expose an endpoint like `/api/case-studies/from-run/:runId/` to create a draft.
- Frontend:
  - Use a **rich-text editor** or markdown editor for the user to refine the draft.
  - Clearly highlight which sections were auto-generated and which are user input.
- For exports:
  - Start with **Markdown export** from backend.
  - Optionally add a PDF generation mechanism later (server-side HTML-to-PDF or an external service).

---

### 6. Data & Analytics Agent

**Purpose**: Define meaningful metrics and show them in an interpretable way.

**Responsibilities**:
- Define scenario-specific **KPIs**:
  - E.g. user activation rate, retention, NPS, revenue, operational cost, time-to-market.
- Ensure every user decision produces **metric signals**:
  - Even if noisy, the direction and magnitude should make sense to learners.
- Provide analytics views for:
  - Metric evolution over the course of a run.
  - Summary of a run at the end (e.g. scoreboard).
  - (Later) progress across multiple runs for a user.

**Tech-specific guidelines**:
- On the backend:
  - Store metrics history as structured data (e.g. `MetricSnapshot` or `Event` models) linked to runs.
- On the frontend:
  - Build **reusable charts and summary components** for metric time series and key KPIs.
  - Use tooltips and labels that **explain** what each metric means and why it matters.

---

### 7. Infrastructure & Quality Agent

**Purpose**: Keep the codebase maintainable, tested, and easy to run.

**Responsibilities**:
- Set up tooling and workflows:
  - **Frontend**: TypeScript strict mode, ESLint, Prettier, testing (e.g. Jest/RTL or Vitest).
  - **Backend**: `pytest`, `black`, `isort`, `ruff` (or equivalents) and a basic test suite.
- Provide simple **developer commands**:
  - For example, `make` targets or npm scripts for `dev`, `test`, `lint`, `format`, and `build`.
- Manage environments:
  - `.env.example` showing necessary environment variables (DB URL, API base URL, secrets).
  - Optional Docker Compose for local dev: Django + Postgres + Redis.

**Tech-specific guidelines**:
- Enforce consistent formatting and linting in CI (or at least with a pre-commit config).
- Separate Django settings into `base.py`, `dev.py`, `prod.py` to simplify deployment.
- Ensure at least **smoke tests** exist for:
  - Critical DRF endpoints used by the React app.
  - Core user flows (e.g. starting a run and making a decision).

---

## How to Use This Document

- **When starting a task**, pick the most relevant agent role(s) and let their responsibilities guide your decisions.
- **When designing a new feature**, check:
  - Which PM learning objectives it supports (Product & Curriculum).
  - How it fits into Django models and DRF APIs (Simulation Design, Backend/API).
  - How it appears and teaches in the React UI (Frontend/UX).
  - How it contributes to better case studies (Case Study & Reporting).
- **When in doubt**, favor:
  - Simplicity and explainability of the simulation.
  - Clear links from decisions → metrics → narrative (case study).

