from django.contrib.admin.apps import AdminConfig


class AltoTecAdminConfig(AdminConfig):
    default_site = "config.admin_site.AltoTecAdminSite"
