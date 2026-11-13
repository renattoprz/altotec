from django.shortcuts import render

from apps.core import notifications, turnstile
from apps.core.ratelimit import ratelimit

from .forms import ArcoForm


@ratelimit("arco", limit=5, window_seconds=3600)
def arco_request(request):
    form = ArcoForm(request.POST if request.method == "POST" else None)
    sent = False
    if request.method == "POST":
        valid = form.is_valid()
        if not turnstile.verify(request):
            form.add_error(None, "No pudimos verificar que no eres un robot. Intenta de nuevo.")
        elif valid:
            arco = form.save()
            notifications.notify_admin(
                "arco_admin", {"arco": arco}, subject=f"Solicitud ARCO: {arco.get_kind_display()}"
            )
            sent = True
            form = ArcoForm()
    return render(request, "legal/arco.html", {"form": form, "sent": sent})
