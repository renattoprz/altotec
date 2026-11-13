import pytest
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice

LOGIN = f"/{settings.ADMIN_URL}login/"


@pytest.fixture
def staff(db):
    user = get_user_model().objects.create_superuser("admin", "a@test.pe", "ClaveMuyLarga-2026!")
    device = TOTPDevice.objects.create(user=user, name="App", confirmed=True)
    return user, device


def _post(client, token):
    return client.post(
        LOGIN,
        {"username": "admin", "password": "ClaveMuyLarga-2026!", "otp_token": token},
    )


def test_login_page_is_single_step_in_spanish(client):
    html = client.get(LOGIN).content.decode()
    assert "Código de verificación" in html
    assert "otp_device" not in html
    assert "otp_challenge" not in html


def test_login_with_totp_without_choosing_device(client, staff):
    _user, device = staff
    token = f"{totp(device.bin_key, device.step, device.t0, device.digits):06d}"
    response = _post(client, token)
    assert response.status_code == 302
    assert client.get(f"/{settings.ADMIN_URL}").status_code == 200


def test_login_rejects_wrong_or_missing_code(client, staff):
    html = _post(client, "000000").content.decode()
    assert "Código incorrecto" in html
    assert "select a device" not in html
    html = _post(client, "").content.decode()
    assert "Ingresa el código" in html


def test_admin_labels_are_spanish():
    assert apps.get_app_config("orders").verbose_name == "Pedidos y envíos"
    assert apps.get_app_config("axes").verbose_name == "Seguridad de acceso"
    attempt = apps.get_model("axes", "AccessAttempt")
    assert attempt._meta.verbose_name_plural == "intentos de acceso fallidos"
