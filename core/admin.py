from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for SiteSettings model.
    """
    list_display = ['site_name', 'maintenance_mode', 'allow_registration', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
