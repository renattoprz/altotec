from django.shortcuts import redirect, render

from apps.core import notifications, turnstile
from apps.core.ratelimit import ratelimit
from apps.orders import services

from .forms import ComplaintForm
from .models import Complaint


@ratelimit("complaint", limit=5, window_seconds=3600)
def complaint_book(request):
    form = ComplaintForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        valid = form.is_valid()
        if not turnstile.verify(request):
            form.add_error(None, "No pudimos verificar que no eres un robot. Intenta de nuevo.")
        elif valid:
            data = form.cleaned_data
            customer = services.save_customer(data, ip=turnstile.client_ip(request))
            complaint = Complaint.objects.create(
                customer=customer,
                kind=data["kind"],
                consumer_address=data["consumer_address"],
                guardian_name=data["guardian_name"],
                order_code=data["order_code"],
                product_or_service=data["product_or_service"],
                amount_pen=data["amount_pen"],
                detail=data["detail"],
                request=data["request"],
            )
            context = {"complaint": complaint}
            notifications.send(
                "complaint_copy",
                context,
                to=[customer.email],
                subject=f"Libro de Reclamaciones · {complaint}",
            )
            notifications.notify_admin(
                "complaint_admin",
                context,
                subject=f"Nuevo {complaint.get_kind_display().lower()} {complaint}",
            )
            request.session["last_complaint"] = complaint.pk
            return redirect("complaints:done")
    return render(request, "complaints/form.html", {"form": form})


def complaint_done(request):
    complaint = Complaint.objects.filter(pk=request.session.get("last_complaint")).first()
    if complaint is None:
        return redirect("complaints:form")
    return render(request, "complaints/done.html", {"complaint": complaint})
