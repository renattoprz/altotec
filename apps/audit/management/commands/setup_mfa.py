"""Crea el dispositivo TOTP (MFA) de un usuario del panel y muestra el QR en la terminal."""

import io

import qrcode
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Configura MFA (app autenticadora) para un usuario del panel."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, username, **options):
        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            raise CommandError("El usuario no existe.")
        TOTPDevice.objects.filter(user=user).delete()
        device = TOTPDevice.objects.create(user=user, name="App autenticadora", confirmed=True)
        qr = qrcode.QRCode(border=1)
        qr.add_data(device.config_url)
        buffer = io.StringIO()
        qr.print_ascii(out=buffer)
        self.stdout.write(buffer.getvalue())
        self.stdout.write(
            self.style.SUCCESS("Escanea el código con Google Authenticator o similar.")
        )
