"""Carga datos de DEMOSTRACIÓN para desarrollo local.

Todo lo creado aquí es ficticio: proveedores, RUC, precios y productos llevan la
marca "DEMO". Las categorías se inspiran en las líneas de equipos POS que
ofrecen los proveedores reales, pero no se copia ningún texto, imagen ni precio.
Nunca ejecutar en producción.
"""

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import Category, Product, Supplier, SupplierOffer
from apps.orders.models import ShippingZone

CATEGORIES = [
    "Ticketeras",
    "Impresoras de etiquetas",
    "Monitores touch",
    "All in One POS",
    "Lectores de código de barras",
    "Gavetas de dinero",
    "Balanzas",
    "Pantallas KDS",
    "Kits POS",
]

SUPPLIERS = [
    ("DEMO Proveedor Uno S.A.C.", "20000000001"),
    ("DEMO Proveedor Dos E.I.R.L.", "20000000002"),
]

ONLINE = Product.SaleMode.ONLINE
QUOTE = Product.SaleMode.QUOTE

# (sku, nombre, categoría, precio S/, costo S/, modo, proveedor, specs)
PRODUCTS = [
    (
        "DEMO-TK80-USB",
        "Ticketera térmica 80 mm USB",
        "Ticketeras",
        "289.00",
        "210.00",
        ONLINE,
        0,
        {"ancho_papel": "80 mm", "conexion": "USB", "velocidad": "250 mm/s", "corte": "automático"},
    ),
    (
        "DEMO-TK80-LAN",
        "Ticketera térmica 80 mm USB + LAN",
        "Ticketeras",
        "349.00",
        "255.00",
        ONLINE,
        0,
        {"ancho_papel": "80 mm", "conexion": "USB, LAN", "velocidad": "300 mm/s"},
    ),
    (
        "DEMO-TK58-BT",
        "Ticketera portátil 58 mm Bluetooth",
        "Ticketeras",
        "199.00",
        "140.00",
        ONLINE,
        1,
        {"ancho_papel": "58 mm", "conexion": "Bluetooth", "bateria": "2000 mAh"},
    ),
    (
        "DEMO-ET-4P",
        "Impresora de etiquetas térmica 4 pulgadas",
        "Impresoras de etiquetas",
        "459.00",
        "330.00",
        ONLINE,
        1,
        {"ancho_etiqueta": "hasta 108 mm", "conexion": "USB"},
    ),
    (
        "DEMO-MT15",
        "Monitor touch 15 pulgadas",
        "Monitores touch",
        "649.00",
        "480.00",
        ONLINE,
        0,
        {"pantalla": '15"', "tactil": "capacitivo", "conexion": "HDMI, VGA, USB"},
    ),
    (
        "DEMO-AIO15-I5",
        'All in One POS 15" Core i5',
        "All in One POS",
        "2499.00",
        "1950.00",
        ONLINE,
        0,
        {"pantalla": '15" touch', "procesador": "Core i5", "ram": "8 GB", "ssd": "256 GB"},
    ),
    (
        "DEMO-AIO15-J",
        'All in One POS 15" Celeron',
        "All in One POS",
        "1699.00",
        "1290.00",
        ONLINE,
        1,
        {"pantalla": '15" touch', "procesador": "Celeron", "ram": "4 GB", "ssd": "128 GB"},
    ),
    (
        "DEMO-LC-USB",
        "Lector de código de barras 1D USB",
        "Lectores de código de barras",
        "89.00",
        "55.00",
        ONLINE,
        1,
        {"tipo": "láser 1D", "conexion": "USB"},
    ),
    (
        "DEMO-LC-2D",
        "Lector de código 2D/QR inalámbrico",
        "Lectores de código de barras",
        "189.00",
        "130.00",
        ONLINE,
        0,
        {"tipo": "imager 2D/QR", "conexion": "inalámbrico 2.4 GHz"},
    ),
    (
        "DEMO-GV-5B",
        "Gaveta de dinero 5 billetes / 8 monedas",
        "Gavetas de dinero",
        "219.00",
        "150.00",
        ONLINE,
        0,
        {"compartimentos": "5 billetes, 8 monedas", "apertura": "RJ11"},
    ),
    (
        "DEMO-BL-30",
        "Balanza comercial 30 kg",
        "Balanzas",
        "329.00",
        "240.00",
        ONLINE,
        1,
        {"capacidad": "30 kg", "division": "5 g", "conexion": "RS232"},
    ),
    (
        "DEMO-KDS-21",
        "Pantalla KDS 21 pulgadas para cocina",
        "Pantallas KDS",
        "1490.00",
        "1100.00",
        QUOTE,
        0,
        {"pantalla": '21" touch', "montaje": "pared o brazo"},
    ),
    (
        "DEMO-KIT-BOD",
        "Kit POS Bodega",
        "Kits POS",
        "1990.00",
        "1500.00",
        QUOTE,
        0,
        {"incluye": "All in One Celeron, ticketera 80 mm, lector 1D, gaveta"},
    ),
    (
        "DEMO-KIT-RES",
        "Kit POS Restaurante",
        "Kits POS",
        "4290.00",
        "3300.00",
        QUOTE,
        0,
        {"incluye": "All in One Core i5, 2 ticketeras LAN, pantalla KDS, gaveta"},
    ),
    (
        "DEMO-KIT-TIE",
        "Kit POS Tienda de ropa",
        "Kits POS",
        "3190.00",
        "2450.00",
        QUOTE,
        1,
        {"incluye": "All in One Core i5, ticketera, impresora de etiquetas, lector 2D, gaveta"},
    ),
]

# Códigos ubigeo: 2 dígitos = departamento, 4 dígitos = provincia. Tarifas DEMO.
ZONES = [
    ("Lima Metropolitana y Callao", ["1501", "07"], "10.00", 1),
    ("Resto de Lima", ["15"], "18.00", 2),
    ("Costa", ["02", "04", "11", "13", "14", "18", "20", "23", "24"], "22.00", 3),
    ("Sierra", ["03", "05", "06", "08", "09", "10", "12", "19", "21"], "28.00", 4),
    ("Selva", ["01", "16", "17", "22", "25"], "35.00", 5),
]


class Command(BaseCommand):
    help = "Carga datos ficticios (DEMO) de catálogo y zonas de envío para desarrollo."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Solo se permite con DEBUG=True (desarrollo local).")
        with transaction.atomic():
            categories = {}
            for order, name in enumerate(CATEGORIES):
                categories[name], _ = Category.objects.get_or_create(
                    slug=slugify(name), defaults={"name": name, "order": order}
                )
            suppliers = [
                Supplier.objects.get_or_create(ruc=ruc, defaults={"business_name": name})[0]
                for name, ruc in SUPPLIERS
            ]
            for sku, name, cat, price, cost, mode, sup, specs in PRODUCTS:
                product, _ = Product.objects.update_or_create(
                    sku=sku,
                    defaults={
                        "name": f"{name} (DEMO)",
                        "slug": slugify(sku),
                        "category": categories[cat],
                        "brand": "Genérica DEMO",
                        "description": "Producto de demostración. No está a la venta.",
                        "specs": specs,
                        "price_pen": Decimal(price),
                        "sale_mode": mode,
                        "published": True,
                    },
                )
                SupplierOffer.objects.update_or_create(
                    product=product,
                    supplier=suppliers[sup],
                    defaults={
                        "cost_pen": Decimal(cost),
                        "stock_confirmed": mode == ONLINE,
                        "confirmed_at": timezone.now() if mode == ONLINE else None,
                    },
                )
            for name, codes, price, days in ZONES:
                ShippingZone.objects.update_or_create(
                    name=name,
                    defaults={
                        "departments": codes,
                        "price_pen": Decimal(price),
                        "lead_time_days": days,
                    },
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"Datos DEMO cargados: {len(CATEGORIES)} categorías, {len(PRODUCTS)} productos, "
                f"{len(ZONES)} zonas de envío."
            )
        )
