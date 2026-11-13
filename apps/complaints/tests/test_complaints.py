from datetime import date

import pytest

from apps.complaints.models import Complaint, add_business_days
from apps.customers.models import Customer


def test_business_days_skip_weekends():
    assert add_business_days(date(2026, 11, 13), 1) == date(2026, 11, 16)  # viernes -> lunes
    assert add_business_days(date(2026, 11, 13), 15) == date(2026, 12, 4)


@pytest.mark.django_db
def test_complaints_get_sequential_numbers():
    customer = Customer.objects.create(
        doc_type="dni", doc_number="45678912", full_name="Ana", email="a@b.pe", phone="999999999"
    )
    common = dict(
        customer=customer,
        kind="reclamo",
        product_or_service="Ticketera",
        detail="No imprime",
        request="Cambio",
    )
    first, second = Complaint.objects.create(**common), Complaint.objects.create(**common)
    assert (first.number, second.number) == (1, 2)
