"""DRF views for simulation app."""
import json
from pathlib import Path

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "CASE_STUDY_TEMPLATE.json"
_template_cache: dict | None = None


def _load_template() -> dict:
    global _template_cache
    if _template_cache is None:
        with open(_TEMPLATE_PATH) as fh:
            _template_cache = json.load(fh)
    return _template_cache

from apps.simulation.models import Scenario, Run, Decision, DecisionGrade, MetricSnapshot
from apps.simulation.services import create_run, submit_decision
from apps.simulation.services.grading import run_grading
from apps.simulation.engine.step import step_engine, EngineInput
from .serializers import (
    ScenarioSerializer,
    RunListSerializer,
    RunDetailSerializer,
    DecisionSubmitSerializer,
    DecisionGradeSerializer,
)


class ScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve scenarios."""

    queryset = Scenario.objects.prefetch_related("learning_objectives")
    serializer_class = ScenarioSerializer


class RunViewSet(viewsets.ModelViewSet):
    """Create, list, retrieve runs. Submit decisions."""

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user).select_related(
            "scenario"
        ).prefetch_related("decisions__grades")

    def get_serializer_class(self):
        if self.action == "list":
            return RunListSerializer
        return RunDetailSerializer

    def create(self, request, *args, **kwargs):
        scenario_id = request.data.get("scenario_id")
        if not scenario_id:
            return Response(
                {"detail": "scenario_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            scenario = Scenario.objects.get(pk=scenario_id)
        except Scenario.DoesNotExist:
            return Response(
                {"detail": "Scenario not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        run = create_run(request.user, scenario)
        serializer = RunDetailSerializer(run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def decisions(self, request, pk=None):
        """Submit a decision for the current step."""
        run = self.get_object()
        serializer = DecisionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {**serializer.validated_data, "step_number": run.step_number}
        try:
            result = submit_decision(run, data)
            return Response(result)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DecisionGradeView(APIView):
    """
    GET  /api/v1/decisions/{id}/grade/  → latest grade (404 if none)
    POST /api/v1/decisions/{id}/grade/  → trigger grading, return grade

    Only the owner of the run may access.
    """

    permission_classes = [IsAuthenticated]

    def _get_decision_for_user(self, pk, user):
        try:
            decision = Decision.objects.select_related("run__scenario").get(pk=pk)
        except Decision.DoesNotExist:
            return None, Response(
                {"detail": "Decision not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if decision.run.user_id != user.id:
            return None, Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )
        return decision, None

    def get(self, request, pk):
        decision, err = self._get_decision_for_user(pk, request.user)
        if err:
            return err
        grade = DecisionGrade.objects.filter(decision=decision).order_by("-created_at").first()
        if grade is None:
            return Response(
                {"detail": "No grade found for this decision."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(DecisionGradeSerializer(grade).data)

    def post(self, request, pk):
        decision, err = self._get_decision_for_user(pk, request.user)
        if err:
            return err
        try:
            grade = run_grading(decision.id)
        except Exception as exc:
            return Response(
                {"detail": f"Grading failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if grade.status == "succeeded" and grade.result_json:
            self._recalculate_metrics(decision, grade)

        http_status = (
            status.HTTP_200_OK if grade.status == "succeeded"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return Response(DecisionGradeSerializer(grade).data, status=http_status)

    def _recalculate_metrics(self, decision, grade):
        """Recalculate the MetricSnapshot for this decision using the LLM grade score."""
        run = decision.run
        step_n = decision.step_number
        quality_override = grade.result_json["overall_score"] / 5.0

        # Previous metrics come from the snapshot at this step (baseline for the decision)
        prev_snapshot = MetricSnapshot.objects.filter(run=run, step_number=step_n).first()
        if prev_snapshot is None:
            return
        prev_metrics = prev_snapshot.metrics

        engine_input = EngineInput(
            state={"metrics": prev_metrics},
            decision={
                "choice_id": decision.payload.get("choice_id", decision.decision_type),
                "rationale": decision.rationale,
            },
            config=run.scenario.config or {},
            step_number=step_n,
            seed=run.seed,
        )
        engine_output = step_engine(engine_input, quality_override=quality_override)

        # Create (or update if it already exists for legacy runs) the snapshot
        # produced by this decision, stored at step_n + 1.
        MetricSnapshot.objects.update_or_create(
            run=run,
            step_number=step_n + 1,
            defaults={"metrics": engine_output.metrics},
        )

        # If this is the latest decision, also update run.state
        has_later_decisions = Decision.objects.filter(run=run, step_number__gt=step_n).exists()
        if not has_later_decisions:
            run.refresh_from_db()
            state = dict(run.state)
            state["metrics"] = engine_output.metrics
            Run.objects.filter(pk=run.pk).update(state=state)


class CaseStudyTemplateView(APIView):
    """
    GET /api/v1/template/           → full base template
    GET /api/v1/template/?role=ai_pm → base template merged with role override hints

    Public endpoint — no auth required.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        template = _load_template()
        role = request.query_params.get("role")
        if role:
            overrides = template.get("role_overrides", {}).get(role)
            if overrides:
                template = {**template, "active_role_override": overrides}
        return Response(template)
