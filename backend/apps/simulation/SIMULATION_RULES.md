# Simulation Rules

This document defines the **game design** of the PM Simulator: how turns work, what decisions look like, and how the world responds.

> This lives in `backend/apps/simulation/` because it is the source of truth for implementing the engine and validating scenario configs.

## Design goals

- Teach real PM decision-making: tradeoffs, ambiguity, stakeholder alignment, outcomes over time
- Keep the simulation **replayable** and **auditable**
- Make it easy to add scenarios without deep code changes (config-driven)

## Key concepts

### Scenario
A scenario is a reusable setup: context, constraints, stakeholders, KPIs, and a set of decision points.

**Scenario has:**
- learning objectives
- initial state (product, market, team, constraints)
- KPI definitions
- stakeholder roster + incentives
- decision point templates (prompts + options + required artifacts)

### Run
A run is a user’s instance of a scenario with a timeline and history.

A run has:
- current step/turn
- state payload (structured JSON)
- history of decisions, events, and metrics

### Turn model

A run proceeds in discrete **turns**. Each turn:

1. Presents context + constraints + decision prompt
2. User submits a decision payload
3. Engine generates:
   - 0..n events
   - 1 metric snapshot
   - updated state and next prompt

Recommended phases (optional):
- Discovery
- Planning
- Execution
- Launch
- Iteration / Incident handling

## Decision schema (DTO)

A decision is the user’s input for a given turn.

Minimum fields:
- `run_id`
- `step_number`
- `decision_type` (e.g., prioritization, experiment_design, stakeholder_alignment)
- `choice_id` or structured fields depending on decision type
- `rationale` (short text, required)
- `assumptions` (list of strings)
- `risks` (list of strings)
- `artifacts` (optional: links/markdown snippets)

Example:
```json
{
  "step_number": 3,
  "decision_type": "prioritization",
  "choice_id": "ship_mvp",
  "rationale": "Deadline is fixed; MVP reduces scope while preserving learning.",
  "assumptions": ["Sales can align enterprise customers on reduced scope"],
  "risks": ["Engineering quality regressions if we rush"],
  "artifacts": {
    "mvp_scope": ["Feature A", "Feature B"],
    "not_doing": ["Feature C"]
  }
}