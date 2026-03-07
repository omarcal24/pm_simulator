from django.contrib import admin
from .models import CaseStudy, CaseStudySection


class CaseStudySectionInline(admin.TabularInline):
    model = CaseStudySection
    extra = 0


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    inlines = [CaseStudySectionInline]
    list_display = ["title", "status", "run", "scenario", "updated_at"]
