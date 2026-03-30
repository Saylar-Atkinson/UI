from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("help/", views.help_page, name="help"),
]
