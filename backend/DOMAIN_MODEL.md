# Domain Model

This document describes the core entities and relationships for the PM Simulator.

## Entities

### Scenario (simulation)
Reusable scenario template.

Key fields:
- `id` (string/uuid)
- `name`
- `version`
- `difficulty`
- `context` (rich text / markdown)
- `config` (JSON) — turns, stakeholders, kpis, initial_state
- `learning_objectives` (M2M)

### LearningObjective (simulation)
- `id`, `name`, `description`

### Run (simulation)
A user's playthrough of a scenario.

Key fields:
- `id`
- `user_id`
- `scenario_id`
- `scenario_version`
- `status` (draft/active/paused/completed/abandoned)
- `seed` (int)
- `step_number` (int)
- `state` (JSON) — source of truth for current world state
- `started_at`, `completed_at`

Invariants:
- Decisions can only be added when `status == active`
- `step_number` is monotonic
- `state` must be updated only via engine outputs (service layer)

### Decision (simulation)
User input per step.

Key fields:
- `id`
- `run_id`
- `step_number`
- `decision_type`
- `payload` (JSON)
- `rationale` (text)
- `created_at`

### Event (simulation)
Notable happenings produced by engine.

Key fields:
- `id`
- `run_id`
- `step_number`
- `type`
- `severity`
- `actor`
- `message`
- `payload` (JSON)
- `created_at`

### MetricSnapshot (simulation)
Time series metric values.

Key fields:
- `id`
- `run_id`
- `step_number`
- `metrics` (JSON) — `{kpi: value}`
- `created_at`

### CaseStudy (cases)
Portfolio artifact derived from a run.

Key fields:
- `id`
- `run_id`
- `scenario_id`
- `title`
- `status` (draft/published)
- `created_at`, `updated_at`

### CaseStudySection (cases)
- `case_study_id`
- `key` (context/problem/constraints/options/decision/results/reflection)
- `content` (markdown)
- `source_refs` (JSON) — pointers to run steps/events/metrics used

### ExportJob (cases) (optional)
- `case_study_id`
- `format` (pdf/md/docx)
- `status`
- `result_url` or storage reference

## Relationships (overview)

- Scenario 1..n Run
- Run 1..n Decision
- Run 1..n Event
- Run 1..n MetricSnapshot
- Run 0..1 CaseStudy
- CaseStudy 1..n CaseStudySection

## Run state machine (summary)

- `active` accepts decisions
- `completed` is read-only
- `paused` blocks decisions but retains state
- `abandoned` blocks decisions and exports may be disabled

## Notes

- Prefer scenario configs to be versioned; runs store the scenario version at start.
- Store enough engine IO to replay/debug: seed + decision payloads + engine outputs per step.