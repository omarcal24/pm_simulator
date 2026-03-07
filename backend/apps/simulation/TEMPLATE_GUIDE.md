# Case Study Template — Developer Guide

## Overview

The case study template system gives users structured guidance before and during a run, while keeping the evaluator flexible and non-prescriptive. The visible template and the internal rubric are **conceptually aligned** but worded independently to preserve scoring validity.

---

## Where things live

| File | Purpose |
|---|---|
| `apps/simulation/CASE_STUDY_TEMPLATE.json` | Single source of truth for all template content |
| `apps/simulation/RUBRIC.md` | Internal scoring rubric (used by grader, not shown verbatim to users) |
| `apps/simulation/GRADER_PROMPT.md` | Grading prompt spec |
| `apps/simulation/ROLE_CARDS.md` | Stakeholder role definitions for scenario-level role scoring |
| `apps/simulation/services/grading.py` | System prompt that references template structure for evaluator alignment |
| `apps/simulation/api/views.py` | `CaseStudyTemplateView` — serves the template JSON |
| `apps/simulation/api/template_urls.py` | Routes `GET /api/v1/template/` |
| `frontend/src/api/template.ts` | API client |
| `frontend/src/components/CaseStudyGuide.tsx` | Collapsible section-by-section template UI |
| `frontend/src/components/ScoringExplainer.tsx` | Collapsible "how you'll be evaluated" UI |

---

## API

### `GET /api/v1/template/`

Returns the full base template. No authentication required.

### `GET /api/v1/template/?role=associate_pm`

Returns the base template with `active_role_override` populated from `role_overrides[role]`.

Available role keys: `associate_pm`, `senior_pm`, `ai_pm`, `growth_pm`

---

## Template JSON structure

```json
{
  "version": "1.0",
  "sections": [ ... ],          // ordered list of template sections
  "what_system_expects": { ... }, // expectations shown to users
  "scoring_dimensions": [ ... ], // visible dimension descriptions
  "scale": { "0": "...", "5": "..." }, // score labels
  "scoring_notes": [ ... ],     // caveats and transparency notes
  "role_overrides": { ... },    // role-specific hints
  "example_good_outline": { ... } // sample strong response
}
```

### Section shape

```json
{
  "key": "problem_statement",
  "title": "Problem Statement",
  "description": "What belongs here...",
  "guiding_questions": ["Q1", "Q2", "Q3"],
  "placeholder": "e.g. ...",
  "required": true
}
```

- `required: true` sections are visually flagged in the UI
- `guiding_questions` are shown when a section is expanded
- `placeholder` is used in the "Insert template scaffold" feature

### Scoring dimension shape

```json
{
  "key": "problem_framing",
  "label": "Problem Framing",
  "description": "What we evaluate...",
  "good_signals": ["Signal 1", "Signal 2"]
}
```

Keys **must match** the dimension keys in `GRADING_SCHEMA.json` (`problem_framing`, `tradeoffs`, `evidence_assumptions`, `execution_realism`, `metrics_success`).

### Role override shape

```json
{
  "label": "Associate PM",
  "focus_note": "What evaluators look for at this level...",
  "section_hints": {
    "proposed_solution": "Role-specific hint for this section"
  },
  "what_we_look_for": ["Question 1", "Question 2"]
}
```

---

## How to add or edit sections

1. Open `CASE_STUDY_TEMPLATE.json`
2. Add a new object to the `sections` array with the required fields (`key`, `title`, `description`, `guiding_questions`, `placeholder`, `required`)
3. Use a unique `key` in snake_case
4. No code changes needed — the frontend renders sections dynamically from the API response

**Important:** Sections are UI-only guidance. Adding a new section does not automatically affect scoring. If you want the evaluator to consider a new dimension, also update `GRADING_SCHEMA.json` and `RUBRIC.md`.

---

## How to add a new role-specific guidance overlay

1. Add a new key under `role_overrides` in `CASE_STUDY_TEMPLATE.json`:

```json
"platform_pm": {
  "label": "Platform PM",
  "focus_note": "...",
  "section_hints": {
    "proposed_solution": "...",
    "risks": "..."
  },
  "what_we_look_for": ["...", "..."]
}
```

2. Call `GET /api/v1/template/?role=platform_pm` to serve it
3. In the frontend, pass `role="platform_pm"` to `getCaseStudyTemplate()` or the `CaseStudyGuide` component

---

## How the visible template relates to internal scoring

The template and the rubric are **aligned in intent** but **not identical in wording**. This is intentional:

- Users see guidance in plain language: "Make a clear recommendation"
- The rubric says: "If G1 (clear recommendation) is false, cap overall_score at 2"
- The grading system prompt references the template section names so the evaluator knows users may have structured their response using them — but does **not penalize** for non-compliance with the template format

### Design principle: substance over format

The evaluator is explicitly instructed:
> "Reward substance and reasoning over structural compliance. Do NOT penalize candidates who did not use these section headers."

This ensures the template is scaffolding, not a mandatory form.

---

## How the "Insert template scaffold" feature works

When a user clicks "Insert template scaffold" in the RunPage:
1. The frontend iterates `template.sections` in order
2. For each section: generates `## {title}\n{placeholder}` as a string
3. The resulting multi-section Markdown scaffold is inserted into the rationale textarea
4. If a role override is active, `section_hints[section.key]` replaces the default placeholder for that section

The scaffold is editable — it's a starting point, not a locked form.

---

## Extending for case type overrides

The current model supports role overrides. To add **case type** overrides (e.g., different guidance for analytics vs. strategy cases):

1. Add a `case_type_overrides` key to the JSON with the same shape as `role_overrides`
2. Extend the backend view to accept a `?case_type=` query param
3. Extend the frontend `getCaseStudyTemplate()` call with the case type

This pattern is already used for role overrides and can be replicated directly.

---

## Design principles

1. **Transparency without gamability** — Users see evaluation dimensions and scale, but not the internal rubric anchors or prompt wording. This builds confidence without making scores trivially predictable.

2. **Flexibility** — The evaluator rewards substance over format. The template is scaffolding, not bureaucracy.

3. **Config-driven** — All content is in JSON. Non-engineers can update sections, hints, and scoring notes without touching code.

4. **Role-aware** — The same base template can surface role-specific guidance overlays without duplicating the underlying structure.

5. **Portfolio usefulness** — Sections like "Reflection & Next Steps" encourage users to think beyond the task, producing responses that translate well into portfolio artifacts.
