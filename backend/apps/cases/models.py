import uuid
from django.db import models

from apps.simulation.models import Run, Scenario


class CaseStudy(models.Model):
    """Portfolio artifact derived from a run."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.OneToOneField(
        Run, on_delete=models.CASCADE, related_name="case_study"
    )
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="case_studies"
    )
    title = models.CharField(max_length=300)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "Case studies"

    def __str__(self):
        return self.title


class CaseStudySection(models.Model):
    """Section of a case study."""

    SECTION_KEYS = [
        "context",
        "problem",
        "constraints",
        "options",
        "decision",
        "execution",
        "results",
        "reflection",
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_study = models.ForeignKey(
        CaseStudy, on_delete=models.CASCADE, related_name="sections"
    )
    key = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    source_refs = models.JSONField(
        default=list,
        help_text="Pointers to run steps/events/metrics used",
    )
    is_auto_generated = models.BooleanField(default=True)

    class Meta:
        ordering = ["key"]
        unique_together = [("case_study", "key")]

    def __str__(self):
        return f"{self.case_study_id} — {self.key}"
