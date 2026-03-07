# Grading Implementation (OpenAI) — v1

This document defines the **production pattern** for role-based grading using the OpenAI API.

It covers:
- request/response structure
- Structured Outputs using JSON Schema
- determinism + audit trail
- error handling + retries
- how to store results in the DB

---

## Why Structured Outputs (JSON Schema)

We require the model output to **exactly match** our grading schema (`GRADING_SCHEMA.json`) to avoid:
- missing fields
- invalid enums
- non-JSON responses

OpenAI provides **Structured Outputs** that enforce JSON Schema compliance. :contentReference[oaicite:0]{index=0}

---

## API choice: Responses API

Use the **Responses API** for new integrations. It supports structured outputs and a cleaner model for tool usage and stored responses. :contentReference[oaicite:1]{index=1}

---

## Inputs we send

We send a single structured "grading bundle" with:
- scenario summary (short)
- roles_in_play + optional role weights
- turn prompt
- candidate response
- run state summary (optional)
- rubric version

Important:
- **Do not** send full internal logs or huge histories. Summarize.
- **Do not** send secrets or PII.

---

## Output contract

The model must output JSON that matches:
- `GRADING_SCHEMA.json` (strict)
- and is consistent with `RUBRIC.md` and `ROLE_CARDS.md`

---

## Recommended model settings

- `temperature`: **0.1–0.3** (low variance)
- `top_p`: default
- `max_output_tokens`: enough for the JSON + reasons (e.g., 800–1500)
- `store`: **false** (recommended unless you explicitly want OpenAI to store responses) :contentReference[oaicite:2]{index=2}

Note: Even with low temperature, grading can drift slightly because content changes within fields are allowed; schema compliance remains guaranteed. :contentReference[oaicite:3]{index=3}

---

## Determinism & audit trail (required)

Persist in DB for every grade:
- `rubric_version`
- `schema_version` (if you version it)
- `model` name
- request parameters (temperature, max_output_tokens)
- the exact input bundle (or a hashed + redacted version)
- the structured JSON result
- timestamps and latency
- optionally: token usage and cost fields (if you capture them)

This enables:
- debugging (“why did this score happen?”)
- regrading when rubric changes
- regression testing

---

## Rate limiting, retries, and fallbacks

### Retry policy
Retry **only** on transient failures:
- 429 rate limit
- 5xx server errors
- network timeouts

Backoff:
- exponential (e.g., 0.5s → 1s → 2s → 4s) with jitter
- max 3–4 retries

### Hard failures (do not retry blindly)
- invalid schema request
- auth errors
- input too large

### Fallback
If LLM grading fails:
- store `status=failed` + error
- return a non-blocking UI message (“grading pending/failed”)
- allow manual re-run

---

## Input preparation (critical)

Create a function that builds a minimal bundle:

- `scenario.context`: cap to ~1k–2k chars
- `run_state`: only the last 1–3 events and latest metrics (or a compact timeline)
- candidate response: include structured fields (choice_id, assumptions, risks) + rationale

Avoid:
- entire turn histories
- raw chat transcripts unless needed

---

## Using Structured Outputs with Responses API

Structured output shape differs between APIs. In Responses API, you set `text.format` to JSON Schema format (strict). :contentReference[oaicite:4]{index=4}

### Pseudocode request (Python)

```python
from openai import OpenAI
import json

client = OpenAI()

def grade_decision(grading_bundle: dict, grading_schema: dict, model: str) -> dict:
    # IMPORTANT: set store=False if you don't want OpenAI to retain the response
    resp = client.responses.create(
        model=model,
        store=False,
        temperature=0.2,
        max_output_tokens=1200,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a strict evaluator of product management decisions. "
                            "Use RUBRIC v1. Be conservative: do not assume unstated facts. "
                            "Output ONLY valid JSON matching the provided schema."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Grade the following decision bundle."},
                    {"type": "text", "text": json.dumps(grading_bundle)},
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "pm_simulator_grade",
                "schema": grading_schema,
                "strict": True,
            }
        },
    )

    # Responses API returns output items; pull the final JSON text payload.
    # Depending on SDK version, you may access it via resp.output_text
    # or by traversing resp.output[]. Keep this adapter in one place.
    output_text = getattr(resp, "output_text", None)
    if not output_text:
        # Fallback traversal (pseudo)
        output_text = resp.output[0].content[0].text

    return json.loads(output_text)