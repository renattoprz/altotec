from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("productos/", views.catalog, name="catalog"),
    path("categoria/<slug:slug>/", views.catalog, name="category"),
    path("producto/<slug:slug>/", views.product_detail, name="product"),
    path("carrito/", views.cart_view, name="cart"),
    path("carrito/actualizar/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("pagar/<str:token>/", views.pay, name="pay"),
    path("pagar/<str:token>/cobrar/", views.charge, name="charge"),
    path("pedido/<str:token>/", views.tracking, name="tracking"),
    path("terminos/", views.page, {"template": "terminos"}, name="terms"),
    path("privacidad/", views.page, {"template": "privacidad"}, name="privacy"),
    path("cambios-y-devoluciones/", views.page, {"template": "devoluciones"}, name="returns"),
    path("envios/", views.page, {"template": "envios"}, name="shipping"),
]
