from django.urls import path
from .views import CaseStudyTemplateView

urlpatterns = [
    path("", CaseStudyTemplateView.as_view(), name="case-study-template"),
]
