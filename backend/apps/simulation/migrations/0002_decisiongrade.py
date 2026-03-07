from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("simulation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DecisionGrade",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("rubric_version", models.CharField(default="1.0", max_length=20)),
                ("model_name", models.CharField(blank=True, max_length=100)),
                ("temperature", models.FloatField(default=0.2)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("result_json", models.JSONField(blank=True, null=True)),
                ("error", models.TextField(blank=True, null=True)),
                ("latency_ms", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "decision",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="simulation.decision",
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="simulation.run",
                    ),
                ),
                (
                    "scenario",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="simulation.scenario",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="decisiongrade",
            index=models.Index(fields=["decision"], name="sim_grade_decision_idx"),
        ),
        migrations.AddIndex(
            model_name="decisiongrade",
            index=models.Index(
                fields=["run", "created_at"], name="sim_grade_run_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="decisiongrade",
            index=models.Index(fields=["status"], name="sim_grade_status_idx"),
        ),
    ]
