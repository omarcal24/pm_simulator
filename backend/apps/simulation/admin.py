from django.contrib import admin
from .models import (
    LearningObjective,
    Scenario,
    Run,
    Decision,
    Event,
    MetricSnapshot,
)

admin.site.register(LearningObjective)
admin.site.register(Scenario)
admin.site.register(Run)
admin.site.register(Decision)
admin.site.register(Event)
admin.site.register(MetricSnapshot)
