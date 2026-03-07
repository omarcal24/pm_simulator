from django.urls import include, path

urlpatterns = [
    path("scenarios/", include("apps.simulation.api.scenarios_urls")),
    path("runs/", include("apps.simulation.api.runs_urls")),
    path("decisions/", include("apps.simulation.api.decisions_urls")),
    path("template/", include("apps.simulation.api.template_urls")),
]
