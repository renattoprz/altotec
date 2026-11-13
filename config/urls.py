from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from apps.orders.webhooks import culqi_webhook


def healthz(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("webhooks/culqi/<str:token>/", culqi_webhook, name="culqi-webhook"),
    path("healthz", healthz),
]
