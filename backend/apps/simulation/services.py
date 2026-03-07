"""
Run services — orchestrate DB + engine + transactions.
"""
from django.utils import timezone

from .engine import step_engine
from .engine.step import EngineInput
from .models import Run, Decision, Event, MetricSnapshot


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
    # Create initial metric snapshot at step 0
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

    expected_step = run.step_number
    step_number = decision_data.get("step_number", expected_step)
    if step_number != expected_step:
        raise ValueError(
            f"Step mismatch: expected {expected_step}, got {step_number}"
        )

    # Create decision record
    decision = Decision.objects.create(
        run=run,
        step_number=step_number,
        decision_type=decision_data.get("decision_type", "general"),
        payload=decision_data,
        rationale=decision_data.get("rationale", ""),
    )

    # Call engine (pure Python)
    engine_input = EngineInput(
        state=dict(run.state),
        decision=decision_data,
        config=run.scenario.config or {},
        step_number=step_number,
        seed=run.seed,
    )
    output = step_engine(engine_input)

    # Persist events
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

    # Persist metric snapshot (for the resulting step after decision)
    next_step = output.next_state.get("step_number", step_number + 1)
    MetricSnapshot.objects.create(
        run=run,
        step_number=next_step,
        metrics=output.metrics,
    )

    # Update run state
    run.state = output.next_state
    run.step_number = output.next_state.get("step_number", run.step_number + 1)

    if output.is_complete:
        run.status = "completed"
        run.completed_at = timezone.now()

    run.save()

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
