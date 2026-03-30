from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="uploadcsv"),
    path("accept/", views.accept_csv, name="accept_csv"),
    path("failed/", views.upload_failed, name="upload_csv_failed"),
    path("failed/invalid_input/", views.invalid_input, name="upload_form_invalid"),
    path("failed/<str:filename>/", views.save_failed, name="save_csv_failed"),
]
