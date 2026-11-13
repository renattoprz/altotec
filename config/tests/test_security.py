import pytest
from django.conf import settings


def test_admin_requires_mfa():
    from django.contrib import admin
    from django_otp.admin import OTPAdminSite

    assert isinstance(admin.site, OTPAdminSite)


def test_admin_url_is_not_default():
    assert settings.ADMIN_URL != "admin/"


def test_cookies_are_not_shared_across_subdomains():
    assert getattr(settings, "SESSION_COOKIE_DOMAIN", None) is None
    assert getattr(settings, "CSRF_COOKIE_DOMAIN", None) is None


@pytest.mark.django_db
def test_security_headers(client):
    response = client.get("/healthz")
    assert response["X-Frame-Options"] == "DENY"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]
