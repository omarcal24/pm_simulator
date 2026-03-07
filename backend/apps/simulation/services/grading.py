"""
LLM-based decision grading service.

Pipeline:
  build_grading_bundle(decision_id) -> dict
  grade_decision_with_openai(bundle) -> dict
  validate_grade_result(result) -> None
  create_or_update_decision_grade(decision_id, result, meta) -> DecisionGrade

  run_grading(decision_id) -> DecisionGrade   ← full pipeline, call from views
"""
import json
import os
import time
from pathlib import Path

import jsonschema

RUBRIC_VERSION = "1.0"
_SCHEMA_PATH = Path(__file__).parent.parent / "GRADING_SCHEMA.json"


def _load_schema() -> dict:
    with open(_SCHEMA_PATH) as fh:
        return json.load(fh)


# Loaded once at module import; safe since it's read-only.
GRADING_SCHEMA: dict = _load_schema()

_SYSTEM_PROMPT = (
    "You are a strict, fair evaluator of product management decisions. "
    "Use RUBRIC v1 as your scoring guide. "
    "Be conservative: if a point is not explicitly stated in the candidate "
    "response, do not assume it. "
    "Score decision quality and judgment, not writing style or length. "
    "If the candidate provides no clear recommendation, overall_score must not "
    "exceed 2. "
    "Candidates may have used a structured template with sections such as "
    "Problem Statement, Assumptions, Goals & Success Metrics, User Perspective, "
    "Proposed Solution, Prioritization & Trade-offs, Execution Plan, Risks & "
    "Mitigations, and Reflection. "
    "Do NOT penalize candidates who did not use these section headers — evaluate "
    "whether the thinking is present, not whether the format was followed. "
    "Reward substance and reasoning over structural compliance. "
    "Output ONLY valid JSON matching the provided schema — no extra text."
)


# ── Bundle builder ────────────────────────────────────────────────────────────

def build_grading_bundle(decision_id) -> dict:
    """
    Compose a minimal grading bundle from DB objects.
    Caps scenario.context at 2 000 chars and run_state at the last 3 events
    to keep the prompt within token budget.
    """
    from apps.simulation.models import Decision

    decision = (
        Decision.objects.select_related("run__scenario", "run")
        .prefetch_related("run__events", "run__metric_snapshots")
        .get(pk=decision_id)
    )
    run = decision.run
    scenario = run.scenario
    config = scenario.config or {}

    kpis = config.get("kpis", [])
    constraints = config.get("constraints", [])
    stakeholders = config.get("stakeholders", [])
    roles_in_play = config.get("roles_in_play", [])
    role_weights = config.get("role_weights", {})

    prompts = config.get("prompts", {})
    turn_prompt = prompts.get(
        str(decision.step_number),
        f"Step {decision.step_number}: Make your decision.",
    )

    # Latest metrics snapshot
    snapshot = (
        run.metric_snapshots.order_by("-step_number").first()
    )
    latest_metrics = snapshot.metrics if snapshot else {}

    # Last 3 events
    recent_events = list(
        run.events.order_by("-step_number", "-created_at")[:3]
    )
    events_summary = [
        {"step": ev.step_number, "type": ev.type, "message": ev.message}
        for ev in reversed(recent_events)
    ]

    payload = decision.payload or {}

    bundle: dict = {
        "rubric_version": RUBRIC_VERSION,
        "scenario": {
            "id": str(scenario.id),
            "name": scenario.name,
            "version": scenario.version,
            "difficulty": scenario.difficulty,
            "context": scenario.context[:2000],
            "kpis": kpis,
            "constraints": constraints if constraints else stakeholders,
            "roles_in_play": roles_in_play,
        },
        "turn": {
            "step_number": decision.step_number,
            "prompt_question": turn_prompt,
        },
        "candidate_response": {
            "decision_type": decision.decision_type,
            "choice_id": payload.get("choice_id", ""),
            "rationale": decision.rationale,
            "assumptions": payload.get("assumptions", []),
            "risks": payload.get("risks", []),
        },
        "run_state": {
            "step_number": run.step_number,
            "metrics": latest_metrics,
            "recent_events": events_summary,
        },
    }

    if role_weights:
        bundle["scenario"]["role_weights"] = role_weights

    return bundle


# ── OpenAI call ───────────────────────────────────────────────────────────────

def grade_decision_with_openai(bundle: dict) -> dict:
    """
    Call the OpenAI Responses API with Structured Outputs.
    Retries on 429 and 5xx (max 3 attempts, exponential back-off).
    """
    try:
        import openai
    except ImportError as exc:
        raise RuntimeError(
            "openai package is not installed. Add it to requirements.txt."
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    model = os.environ.get("OPENAI_GRADER_MODEL", "gpt-4o")
    temperature = float(os.environ.get("OPENAI_GRADER_TEMPERATURE", "0.2"))

    client = openai.OpenAI(api_key=api_key)
    user_text = json.dumps(bundle, indent=2)

    max_retries = 3
    last_exc: Exception | None = None

    for attempt in range(max_retries):
        try:
            resp = client.responses.create(
                model=model,
                store=False,
                temperature=temperature,
                max_output_tokens=1400,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": _SYSTEM_PROMPT}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Grade the following PM decision bundle:\n\n" + user_text,
                            },
                        ],
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "pm_simulator_grade",
                        "schema": GRADING_SCHEMA,
                        "strict": True,
                    }
                },
            )

            # SDK ≥ 1.66: resp.output_text; older: traverse output list
            output_text = getattr(resp, "output_text", None)
            if not output_text:
                output_text = resp.output[0].content[0].text

            return json.loads(output_text)

        except openai.RateLimitError as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                time.sleep(0.5 * (2**attempt))
        except openai.APIStatusError as exc:
            last_exc = exc
            if exc.status_code >= 500 and attempt < max_retries - 1:
                time.sleep(0.5 * (2**attempt))
            else:
                raise
        except openai.APIConnectionError as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                time.sleep(0.5 * (2**attempt))
            else:
                raise

    raise last_exc  # type: ignore[misc]


# ── Schema validation ─────────────────────────────────────────────────────────

def validate_grade_result(result: dict) -> None:
    """Raise jsonschema.ValidationError if result does not match GRADING_SCHEMA."""
    jsonschema.validate(instance=result, schema=GRADING_SCHEMA)


# ── Persistence ───────────────────────────────────────────────────────────────

def create_or_update_decision_grade(
    decision_id, result: dict, meta: dict
):
    """
    Upsert a DecisionGrade row for this decision.
    meta keys: rubric_version, model_name, temperature, latency_ms.
    """
    from apps.simulation.models import Decision, DecisionGrade

    decision = Decision.objects.select_related("run__scenario").get(pk=decision_id)
    grade, _ = DecisionGrade.objects.update_or_create(
        decision=decision,
        defaults={
            "run": decision.run,
            "scenario": decision.run.scenario,
            "rubric_version": meta.get("rubric_version", RUBRIC_VERSION),
            "model_name": meta.get("model_name", ""),
            "temperature": meta.get("temperature", 0.2),
            "status": "succeeded",
            "result_json": result,
            "error": None,
            "latency_ms": meta.get("latency_ms"),
        },
    )
    return grade


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_grading(decision_id):
    """
    Full grading pipeline (synchronous).
    Creates a DecisionGrade, runs the LLM call, persists result.
    Safe to call from a view; on any failure sets status=failed.
    """
    from apps.simulation.models import Decision, DecisionGrade

    decision = Decision.objects.select_related("run__scenario").get(pk=decision_id)
    model_name = os.environ.get("OPENAI_GRADER_MODEL", "gpt-4o")
    temperature = float(os.environ.get("OPENAI_GRADER_TEMPERATURE", "0.2"))

    grade = DecisionGrade.objects.create(
        decision=decision,
        run=decision.run,
        scenario=decision.run.scenario,
        rubric_version=RUBRIC_VERSION,
        model_name=model_name,
        temperature=temperature,
        status="pending",
    )

    t0 = time.monotonic()
    try:
        bundle = build_grading_bundle(decision_id)
        result = grade_decision_with_openai(bundle)
        validate_grade_result(result)
        grade.status = "succeeded"
        grade.result_json = result
        grade.error = None
    except Exception as exc:
        grade.status = "failed"
        grade.error = str(exc)
        grade.result_json = None
    finally:
        grade.latency_ms = int((time.monotonic() - t0) * 1000)
        grade.save()

    return grade
