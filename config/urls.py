from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.customers.views import arco_request
from apps.orders.webhooks import culqi_webhook


def healthz(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("webhooks/culqi/<str:token>/", culqi_webhook, name="culqi-webhook"),
    path("healthz", healthz),
    path("cotizar/", include("apps.quotes.urls")),
    path("libro-de-reclamaciones/", include("apps.complaints.urls")),
    path("derechos-arco/", arco_request, name="arco"),
    path("", include("apps.store.urls")),
]

handler404 = "apps.store.errors.not_found"
handler500 = "apps.store.errors.server_error"
