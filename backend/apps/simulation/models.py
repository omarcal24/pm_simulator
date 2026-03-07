import uuid
from django.db import models

from apps.accounts.models import User


class LearningObjective(models.Model):
    """Learning objective for scenarios."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Scenario(models.Model):
    """Reusable scenario template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
    )
    context = models.TextField(help_text="Rich text / markdown context")
    config = models.JSONField(
        default=dict,
        help_text="turns, stakeholders, kpis, initial_state",
    )
    learning_objectives = models.ManyToManyField(
        LearningObjective, blank=True, related_name="scenarios"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (v{self.version})"


class Run(models.Model):
    """A user's playthrough of a scenario."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="runs")
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="runs"
    )
    scenario_version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active"
    )
    seed = models.IntegerField(default=0)
    step_number = models.PositiveIntegerField(default=0)
    state = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.scenario.name} — Run by {self.user}"


class Decision(models.Model):
    """User input per step."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="decisions")
    step_number = models.PositiveIntegerField()
    decision_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    rationale = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number"]
        unique_together = [("run", "step_number")]

    def __str__(self):
        return f"Decision {self.step_number} for run {self.run_id}"


class Event(models.Model):
    """Notable happenings produced by engine."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="events")
    step_number = models.PositiveIntegerField()
    type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, default="info")
    actor = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number", "created_at"]

    def __str__(self):
        return f"{self.type}: {self.message[:50]}..."


class MetricSnapshot(models.Model):
    """Time series metric values."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        Run, on_delete=models.CASCADE, related_name="metric_snapshots"
    )
    step_number = models.PositiveIntegerField()
    metrics = models.JSONField(default=dict)  # {kpi: value}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number"]

    def __str__(self):
        return f"Metrics step {self.step_number} for run {self.run_id}"


class DecisionGrade(models.Model):
    """LLM-generated grade for a single decision."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(
        Decision, on_delete=models.CASCADE, related_name="grades"
    )
    # Denormalized for convenience
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="grades")
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="grades", null=True
    )
    rubric_version = models.CharField(max_length=20, default="1.0")
    model_name = models.CharField(max_length=100, blank=True)
    temperature = models.FloatField(default=0.2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    result_json = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["decision"]),
            models.Index(fields=["run", "created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Grade({self.status}) for decision {self.decision_id}"
