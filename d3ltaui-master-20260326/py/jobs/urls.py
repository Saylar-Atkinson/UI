from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="jobs"),
    path("search/", views.search, name="job_search"),
    path("<str:job_id>/", views.status, name="job_status"),
    path("api/job/<str:job_id>/", views.status_minimal, name="job_status_api"),
    path("<str:job_id>/cluster/<str:cluster_id>/", views.cluster_preview, name="cluster_preview"),
]
