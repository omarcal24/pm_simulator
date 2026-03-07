"""
Run services — orchestrate DB + engine + transactions.
Re-exported from this package so existing imports continue to work.
"""
from django.utils import timezone

from apps.simulation.engine import step_engine
from apps.simulation.engine.step import EngineInput
from apps.simulation.models import Run, Decision, Event, MetricSnapshot


def create_run(user, scenario) -> Run:
    """Create a new run for a user and scenario."""
    config = scenario.config or {}
    initial_state = {
        "step_number": 0,
        "metrics": config.get("initial_metrics", {}),
        "prompt": config.get("prompts", {}).get(
            "0",
            "Welcome! Review the context and make your first decision.",
        ),
    }
    run = Run.objects.create(
        user=user,
        scenario=scenario,
        scenario_version=scenario.version,
        status="active",
        seed=hash(str(user.id) + str(scenario.id)) % (2**31),
        step_number=0,
        state=initial_state,
    )
    kpis = config.get("kpis", ["activation_rate", "retention_30d"])
    initial_metrics = config.get("initial_metrics", {k: 50.0 for k in kpis})
    MetricSnapshot.objects.create(
        run=run,
        step_number=0,
        metrics=initial_metrics,
    )
    return run


def submit_decision(run: Run, decision_data: dict) -> dict:
    """
    Submit a decision for the current step. Returns updated run state,
    events, and metrics.
    """
    if run.status != "active":
        raise ValueError(f"Run is not active (status={run.status})")

    # Require all previous decisions to be graded before accepting a new one.
    ungraded = run.decisions.exclude(grades__status="succeeded").exists()
    if ungraded:
        raise ValueError("Grade your previous decision before submitting the next one.")

    expected_step = run.step_number
    step_number = decision_data.get("step_number", expected_step)
    if step_number != expected_step:
        raise ValueError(
            f"Step mismatch: expected {expected_step}, got {step_number}"
        )

    decision = Decision.objects.create(
        run=run,
        step_number=step_number,
        decision_type=decision_data.get("decision_type", "general"),
        payload=decision_data,
        rationale=decision_data.get("rationale", ""),
    )

    engine_input = EngineInput(
        state=dict(run.state),
        decision=decision_data,
        config=run.scenario.config or {},
        step_number=step_number,
        seed=run.seed,
    )
    output = step_engine(engine_input)

    for ev in output.events:
        Event.objects.create(
            run=run,
            step_number=step_number,
            type=ev.type,
            severity=ev.severity,
            actor=ev.actor,
            message=ev.message,
            payload=ev.payload,
        )

    # MetricSnapshot is NOT created here — it is created after the decision is graded.
    # KPIs only update when the grade quality score is known.
    # Preserve the current metrics in state so the next step starts from the last
    # graded values, not provisional keyword-heuristic values.
    prev_metrics = run.state.get("metrics", {})
    next_state = output.next_state
    next_state["metrics"] = prev_metrics

    run.state = next_state
    run.step_number = next_state.get("step_number", run.step_number + 1)

    if output.is_complete:
        run.status = "completed"
        run.completed_at = timezone.now()

    run.save()

    # TODO: set AUTO_GRADE_ON_DECISION=true in env to trigger async grading here.

    return {
        "run_id": str(run.id),
        "step_number": run.step_number,
        "events": [
            {
                "type": e.type,
                "severity": e.severity,
                "actor": e.actor,
                "message": e.message,
            }
            for e in output.events
        ],
        "metrics": output.metrics,
        "next_prompt": output.next_prompt,
        "is_complete": output.is_complete,
    }
