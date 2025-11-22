from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "🏆 Tejos Olímpica - Administración"
    site_title = "Panel Admin"
    index_title = "Panel de Control"