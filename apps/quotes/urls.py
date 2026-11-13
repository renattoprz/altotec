from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.request_quote, name="request"),
    path("enviada/", views.quote_sent, name="sent"),
    path("pagar/<str:token>/", views.pay_quote, name="pay"),
]
