"""API v1 URL configuration."""
from django.urls import include, path

urlpatterns = [
    path("", include("apps.simulation.api.urls")),
    path("case-studies/", include("apps.cases.api.urls")),
    path("", include("apps.accounts.api.urls")),
]
