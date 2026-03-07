# API Spec (Draft)

This is a **draft** contract for the Django REST Framework API.

Base path: `/api/v1`

## Conventions

- JSON only
- Errors:
  - `400` validation: `{ "detail": "...", "fields": { "field": ["msg"] } }`
  - `401/403` auth: `{ "detail": "Not authenticated." }` / `{ "detail": "Permission denied." }`

## Resources

### Decision Grades

#### Get latest grade for a decision
`GET /decisions/{id}/grade/`

Auth: session (owner of the run only). Returns `404` if no grade exists yet.

Response:
```json
{
  "id": "uuid",
  "decision": "uuid",
  "run": "uuid",
  "rubric_version": "1.0",
  "model_name": "gpt-4o",
  "temperature": 0.2,
  "status": "succeeded",
  "result_json": {
    "rubric_version": "1.0",
    "overall_score": 3.4,
    "universal_score": 3.4,
    "dimension_scores": [
      { "key": "problem_framing", "score": 3, "reason": "..." },
      { "key": "tradeoffs", "score": 4, "reason": "..." },
      { "key": "evidence_assumptions", "score": 3, "reason": "..." },
      { "key": "execution_realism", "score": 3, "reason": "..." },
      { "key": "metrics_success", "score": 4, "reason": "..." }
    ],
    "role_scores": [],
    "gates": {
      "has_clear_recommendation": true,
      "mentions_constraints": true,
      "mentions_success_metrics": true,
      "mentions_risks_and_mitigation": false,
      "compares_alternatives": true
    },
    "strengths": ["Clear recommendation", "Good metric framing"],
    "improvements": ["Add risk mitigation plan"],
    "red_flags": [],
    "confidence": 0.85
  },
  "error": null,
  "latency_ms": 1240,
  "created_at": "2026-03-06T17:00:00Z",
  "updated_at": "2026-03-06T17:00:01Z"
}
```

#### Trigger grading for a decision
`POST /decisions/{id}/grade/`

Auth: session (owner of the run only). Runs grading synchronously.
Returns `200` on success, `422` if grading failed (LLM error stored in `error` field).

Body: `{}` (empty — no input needed)

Response: same shape as GET above.

---

### Scenarios

#### List scenarios
`GET /scenarios/`

Response (example):
```json
[
  {
    "id": "scn_001",
    "name": "B2B Onboarding Drop",
    "difficulty": "intermediate",
    "learning_objectives": ["prioritization", "stakeholder management"],
    "kpis": ["activation_rate", "retention_30d"]
  }
]