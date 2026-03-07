from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.cases.models import CaseStudy, CaseStudySection
from apps.cases.api.views import CaseStudyViewSet
from apps.simulation.models import Run


@api_view(["POST"])
def from_run(request, run_id):
    """Create a case study draft from a completed run."""
    try:
        run = Run.objects.get(pk=run_id, user=request.user)
    except Run.DoesNotExist:
        return Response(
            {"detail": "Run not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if run.status != "completed":
        return Response(
            {"detail": "Run must be completed to create a case study"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if hasattr(run, "case_study"):
        cs = run.case_study
        return Response(
            {
                "id": str(cs.id),
                "title": cs.title,
                "sections": [
                    {"key": s.key, "content": s.content}
                    for s in cs.sections.all()
                ],
            }
        )
    case_study = create_case_study_from_run(run)
    return Response(
        {
            "id": str(case_study.id),
            "title": case_study.title,
            "sections": [
                {"key": s.key, "content": s.content}
                for s in case_study.sections.all()
            ],
        },
        status=status.HTTP_201_CREATED,
    )


def create_case_study_from_run(run):
    """Generate a case study draft from run history."""
    scenario = run.scenario
    config = scenario.config or {}
    title = f"{scenario.name} — Simulation Case Study"
    case_study = CaseStudy.objects.create(
        run=run,
        scenario=scenario,
        title=title,
        status="draft",
    )

    decisions = list(run.decisions.all())
    snapshots = list(run.metric_snapshots.all())
    prompts = config.get("prompts", {})
    initial_metrics = config.get("initial_metrics", {})
    stakeholders = config.get("stakeholders", [])

    # context — full scenario markdown
    context_content = scenario.context or ""

    # problem — first meaningful paragraph from context
    context_lines = [l for l in context_content.split("\n") if l.strip() and not l.startswith("#")]
    problem_content = context_lines[0] if context_lines else scenario.name

    # constraints — initial KPIs + stakeholders from config
    constraints_parts = []
    if initial_metrics:
        constraints_parts.append("**Starting KPIs:**")
        for k, v in initial_metrics.items():
            constraints_parts.append(f"- {k.replace('_', ' ').title()}: {v}")
    if stakeholders:
        constraints_parts.append("\n**Key stakeholders:**")
        for s in stakeholders:
            constraints_parts.append(f"- {s}")
    constraints_content = "\n".join(constraints_parts) if constraints_parts else "No constraints recorded."

    # options — step prompts showing the challenges/questions at each step
    if prompts and decisions:
        options_parts = []
        for d in decisions:
            prompt_text = prompts.get(str(d.step_number), "")
            if prompt_text:
                options_parts.append(f"**Step {d.step_number + 1}:** {prompt_text}")
        options_content = "\n\n".join(options_parts) if options_parts else "No step prompts recorded."
    else:
        options_content = "No step prompts recorded."

    # decision — each step with its prompt and full rationale, properly separated
    if decisions:
        decision_parts = []
        for d in decisions:
            prompt_text = prompts.get(str(d.step_number), "")
            lines = [f"### Step {d.step_number + 1}"]
            if prompt_text:
                lines.append(f"**Prompt:** {prompt_text}\n")
            lines.append(f"**My decision:** {d.rationale}")
            decision_parts.append("\n".join(lines))
        decision_content = "\n\n".join(decision_parts)
    else:
        decision_content = "No decisions recorded."

    # execution — metric changes per step
    if snapshots and len(snapshots) > 1:
        exec_parts = []
        for i in range(1, len(snapshots)):
            prev = snapshots[i - 1].metrics
            curr = snapshots[i].metrics
            step_num = snapshots[i].step_number
            deltas = []
            for k in curr:
                delta = curr[k] - prev.get(k, curr[k])
                sign = "+" if delta >= 0 else ""
                deltas.append(f"{k.replace('_', ' ').title()}: {curr[k]:.1f} ({sign}{delta:.1f})")
            exec_parts.append(f"**After step {step_num + 1}:** " + ", ".join(deltas))
        execution_content = "\n\n".join(exec_parts)
    elif snapshots:
        metrics_str = ", ".join(
            f"{k.replace('_', ' ').title()}: {v}" for k, v in snapshots[0].metrics.items()
        )
        execution_content = f"**Baseline:** {metrics_str}"
    else:
        execution_content = "No metric history recorded."

    # results — final state vs baseline
    if snapshots:
        baseline = snapshots[0].metrics
        final = snapshots[-1].metrics
        results_parts = ["**Final results vs. baseline:**\n"]
        for k in final:
            delta = final[k] - baseline.get(k, final[k])
            sign = "+" if delta >= 0 else ""
            results_parts.append(
                f"- {k.replace('_', ' ').title()}: {final[k]:.1f} "
                f"(baseline {baseline.get(k, '?')}, {sign}{delta:.1f})"
            )
        results_content = "\n".join(results_parts)
    else:
        results_content = "No metric data recorded."

    # reflection — placeholder for user to fill in
    reflection_content = (
        "Describe what you learned from this simulation and what you would do differently next time.\n\n"
        "Consider:\n"
        "- Which decisions had the most impact on the KPIs?\n"
        "- What trade-offs were hardest to navigate?\n"
        "- What would you change if you ran this scenario again?"
    )

    sections_data = [
        ("context", context_content),
        ("problem", problem_content),
        ("constraints", constraints_content),
        ("options", options_content),
        ("decision", decision_content),
        ("execution", execution_content),
        ("results", results_content),
        ("reflection", reflection_content),
    ]
    for key, content in sections_data:
        CaseStudySection.objects.create(
            case_study=case_study,
            key=key,
            content=content,
            is_auto_generated=True,
        )
    return case_study


router = DefaultRouter()
router.register(r"", CaseStudyViewSet, basename="casestudy")

urlpatterns = [
    path("from-run/<uuid:run_id>/", from_run),
    path("", include(router.urls)),
]
