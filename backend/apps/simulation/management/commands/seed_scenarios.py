"""Seed sample scenarios for development."""
from django.core.management.base import BaseCommand
from apps.simulation.models import LearningObjective, Scenario


class Command(BaseCommand):
    help = "Seed sample scenarios"

    def handle(self, *args, **options):
        obj, _ = LearningObjective.objects.get_or_create(
            name="prioritization",
            defaults={"description": "Practice prioritization under constraints"},
        )
        obj2, _ = LearningObjective.objects.get_or_create(
            name="stakeholder management",
            defaults={"description": "Align stakeholders with competing interests"},
        )
        b2b, created = Scenario.objects.get_or_create(
            name="B2B Onboarding Drop",
            defaults={
                "version": 1,
                "difficulty": "intermediate",
                "context": """## B2B Onboarding Drop

You are the PM for a B2B SaaS product. Activation rates have dropped 15% in the last quarter. Your VP wants a plan in 2 weeks.

**Key stakeholders:**
- Engineering: wants to fix tech debt first
- Sales: needs a quick win for enterprise pipeline
- Support: reports confusion in onboarding flows

**KPIs tracked in this simulation:**
- **Activation rate** — percentage of new accounts that reach the "activated" state (completed key onboarding steps). Starts at 45/100.
- **Retention (30d)** — percentage of activated users still active 30 days later. Starts at 62/100.

Both are 0–100 index scores. Higher is better. Your decisions will move them up or down based on what you prioritize.
""",
                "config": {
                    "kpis": ["activation_rate", "retention_30d"],
                    "max_steps": 5,
                    "initial_metrics": {"activation_rate": 45.0, "retention_30d": 62.0},
                    "stakeholders": ["Engineering", "Sales", "Support"],
                    "prompts": {
                        "0": "You've just joined. Review the context. Your first decision: do you prioritize a quick win (Sales) or deeper investigation (Engineering)?",
                        "1": "Initial discovery complete. Activation correlates with step 3 drop-off. Do you ship a quick fix or run an experiment?",
                        "2": "Experiments show confusion in the enterprise flow. Do you scope down the fix for SMB only or invest in both segments?",
                        "3": "Sales is pushing for a demo. Do you delay to complete the fix or ship partial and iterate?",
                        "4": "Final step. Summarize your approach and expected impact.",
                    },
                },
            },
        )
        if created:
            b2b.learning_objectives.add(obj, obj2)

        feature, created = Scenario.objects.get_or_create(
            name="Feature Launch Under Deadline",
            defaults={
                "version": 1,
                "difficulty": "beginner",
                "context": """## Feature Launch Under Deadline

Your team has 6 weeks to ship a key feature. Scope creep is already a risk.

**Key stakeholders:**
- Engineering: concerned about technical debt and test coverage
- Design: wants another iteration on the core flow

**KPIs tracked in this simulation:**
- **Schedule health** — how on-track the team is relative to the original plan. Starts at 70/100 (some early scope slip). Higher = healthier delivery timeline.
- **Quality index** — a composite of code quality, bug rate, and test coverage signals. Starts at 55/100. Higher = fewer defects, more maintainable code.

Both are 0–100 index scores. Speed-focused decisions tend to improve schedule health but hurt quality; quality-focused decisions do the reverse. Your job is to find the right balance.
""",
                "config": {
                    "kpis": ["schedule_health", "quality_index"],
                    "max_steps": 4,
                    "initial_metrics": {"schedule_health": 70.0, "quality_index": 55.0},
                    "stakeholders": ["Engineering", "Design"],
                    "prompts": {
                        "0": "Kickoff. The team estimates 6 weeks but the roadmap shows 5. What's your first move?",
                        "1": "Design wants another iteration on the core flow. Do you push back or accommodate?",
                        "2": "Engineering found a critical bug mid-sprint. Ship on time with the bug or delay to fix it?",
                        "3": "Final checkpoint. How did you balance scope, time, and quality? What would you do differently?",
                    },
                },
            },
        )
        if created:
            feature.learning_objectives.add(obj)

        self.stdout.write(self.style.SUCCESS("Scenarios seeded."))
