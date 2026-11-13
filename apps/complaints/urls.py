from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.complaint_book, name="form"),
    path("registrado/", views.complaint_done, name="done"),
]
