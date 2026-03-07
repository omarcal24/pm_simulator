from django.urls import path

from .views import DecisionGradeView

urlpatterns = [
    path("<uuid:pk>/grade/", DecisionGradeView.as_view(), name="decision-grade"),
]
