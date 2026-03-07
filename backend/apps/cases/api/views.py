"""DRF views for case studies."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cases.models import CaseStudy, CaseStudySection
from .serializers import CaseStudySerializer, CaseStudySectionSerializer


class CaseStudyViewSet(viewsets.ModelViewSet):
    """Retrieve and update case studies."""

    serializer_class = CaseStudySerializer

    def get_queryset(self):
        return CaseStudy.objects.filter(run__user=self.request.user).select_related(
            "run", "scenario"
        ).prefetch_related("sections")

    def destroy(self, request, *args, **kwargs):
        # Allow delete
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["patch"])
    def sections(self, request, pk=None):
        """Bulk update section content."""
        case_study = self.get_object()
        sections_data = request.data.get("sections", [])
        for item in sections_data:
            key = item.get("key")
            content = item.get("content")
            if key and content is not None:
                CaseStudySection.objects.filter(
                    case_study=case_study, key=key
                ).update(content=content)
        return Response(CaseStudySerializer(case_study).data)

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Export case study as Markdown."""
        section_order = ["context", "problem", "constraints", "options", "decision", "execution", "results", "reflection"]
        case_study = self.get_object()
        md = f"# {case_study.title}\n\n"
        sections = {s.key: s for s in case_study.sections.all()}
        for key in section_order:
            section = sections.get(key)
            if section and section.content and section.content.strip():
                label = key.replace("_", " ").title()
                md += f"## {label}\n\n{section.content}\n\n"
        return Response({"markdown": md, "title": case_study.title})

    @action(detail=True, methods=["get"], url_path="learning-report")
    def learning_report(self, request, pk=None):
        """Export a learning report with full context, step questions, answers, and grades."""
        case_study = self.get_object()
        run = case_study.run
        scenario = case_study.scenario
        config = scenario.config or {}
        prompts = config.get("prompts", {})

        decisions = list(run.decisions.prefetch_related("grades").all())

        md = f"# Learning Report: {scenario.name}\n\n"
        md += f"*Scenario: {scenario.name} | Difficulty: {scenario.difficulty}*\n\n"
        md += "---\n\n"

        md += "## Scenario Context\n\n"
        md += (scenario.context or "") + "\n\n"
        md += "---\n\n"

        for d in decisions:
            prompt_text = prompts.get(str(d.step_number), "")
            md += f"## Step {d.step_number + 1}\n\n"
            if prompt_text:
                md += f"**Question:** {prompt_text}\n\n"
            md += f"**Your Answer:**\n\n{d.rationale}\n\n"

            grade = d.grades.filter(status="succeeded").first()
            if grade and grade.result_json:
                r = grade.result_json
                md += f"**AI Grade:** {r.get('overall_score', 'N/A')}/5\n\n"

                dims = r.get("dimension_scores", [])
                if dims:
                    md += "**Dimension Scores:**\n\n"
                    for dim in dims:
                        label = dim["key"].replace("_", " ").title()
                        md += f"- {label}: {dim['score']}/5 — {dim['reason']}\n"
                    md += "\n"

                strengths = r.get("strengths", [])
                if strengths:
                    md += "**Strengths:**\n\n"
                    for s in strengths:
                        md += f"- {s}\n"
                    md += "\n"

                improvements = r.get("improvements", [])
                if improvements:
                    md += "**Areas for Improvement:**\n\n"
                    for imp in improvements:
                        md += f"- {imp}\n"
                    md += "\n"

                red_flags = r.get("red_flags", [])
                if red_flags:
                    md += "**Red Flags:**\n\n"
                    for rf in red_flags:
                        md += f"- {rf}\n"
                    md += "\n"
            else:
                md += "*This step was not graded.*\n\n"

            md += "---\n\n"

        return Response({"markdown": md, "title": f"Learning Report — {scenario.name}"})
