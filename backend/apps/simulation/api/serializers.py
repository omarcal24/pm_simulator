"""DRF serializers for simulation app."""
from rest_framework import serializers

from apps.simulation.models import (
    Scenario,
    LearningObjective,
    Run,
    Decision,
    DecisionGrade,
    Event,
    MetricSnapshot,
)


class LearningObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObjective
        fields = ["id", "name", "description"]


class ScenarioSerializer(serializers.ModelSerializer):
    learning_objectives = LearningObjectiveSerializer(many=True, read_only=True)
    kpis = serializers.SerializerMethodField()

    class Meta:
        model = Scenario
        fields = [
            "id",
            "name",
            "version",
            "difficulty",
            "context",
            "config",
            "learning_objectives",
            "kpis",
        ]

    def get_kpis(self, obj):
        return obj.config.get("kpis", [])


class RunListSerializer(serializers.ModelSerializer):
    scenario_name = serializers.CharField(source="scenario.name", read_only=True)

    class Meta:
        model = Run
        fields = [
            "id",
            "scenario",
            "scenario_name",
            "status",
            "step_number",
            "started_at",
            "completed_at",
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "step_number", "type", "severity", "actor", "message"]


class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = ["id", "step_number", "metrics", "created_at"]


class DecisionSerializer(serializers.ModelSerializer):
    grade_status = serializers.SerializerMethodField()

    class Meta:
        model = Decision
        fields = ["id", "step_number", "decision_type", "rationale", "created_at", "grade_status"]

    def get_grade_status(self, obj):
        """Return 'succeeded', 'pending', or None based on existing grades."""
        for g in obj.grades.all():
            if g.status == "succeeded":
                return "succeeded"
        for g in obj.grades.all():
            if g.status == "pending":
                return "pending"
        return None


class RunDetailSerializer(serializers.ModelSerializer):
    scenario_name = serializers.CharField(source="scenario.name", read_only=True)
    scenario_context = serializers.CharField(source="scenario.context", read_only=True)
    scenario_difficulty = serializers.CharField(source="scenario.difficulty", read_only=True)
    scenario_learning_objectives = LearningObjectiveSerializer(
        source="scenario.learning_objectives", many=True, read_only=True
    )
    events = EventSerializer(many=True, read_only=True)
    metric_snapshots = MetricSnapshotSerializer(many=True, read_only=True)
    decisions = DecisionSerializer(many=True, read_only=True)
    current_prompt = serializers.SerializerMethodField()
    kpis = serializers.SerializerMethodField()

    class Meta:
        model = Run
        fields = [
            "id",
            "scenario",
            "scenario_name",
            "scenario_context",
            "scenario_difficulty",
            "scenario_learning_objectives",
            "status",
            "step_number",
            "state",
            "seed",
            "started_at",
            "completed_at",
            "current_prompt",
            "kpis",
            "decisions",
            "events",
            "metric_snapshots",
        ]

    def get_current_prompt(self, obj):
        prompts = obj.scenario.config.get("prompts", {})
        step = str(obj.step_number)
        return prompts.get(
            step,
            obj.state.get(
                "prompt",
                f"Step {obj.step_number}: Make your decision based on the context and metrics.",
            ),
        )

    def get_kpis(self, obj):
        return obj.scenario.config.get("kpis", [])


class DecisionGradeSerializer(serializers.ModelSerializer):
    """Serializes a DecisionGrade for API output."""

    class Meta:
        model = DecisionGrade
        fields = [
            "id",
            "decision",
            "run",
            "rubric_version",
            "model_name",
            "temperature",
            "status",
            "result_json",
            "error",
            "latency_ms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DecisionSubmitSerializer(serializers.Serializer):
    decision_type = serializers.CharField(required=True)
    choice_id = serializers.CharField(required=False, allow_blank=True)
    rationale = serializers.CharField(required=True)
    assumptions = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    risks = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    artifacts = serializers.JSONField(required=False, default=dict)
