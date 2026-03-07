"""DRF serializers for case studies."""
from rest_framework import serializers

from apps.cases.models import CaseStudy, CaseStudySection


class CaseStudySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStudySection
        fields = ["id", "key", "content", "is_auto_generated"]


class CaseStudySerializer(serializers.ModelSerializer):
    sections = CaseStudySectionSerializer(many=True, read_only=True)

    class Meta:
        model = CaseStudy
        fields = [
            "id",
            "run",
            "scenario",
            "title",
            "status",
            "sections",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["run", "scenario", "created_at"]
