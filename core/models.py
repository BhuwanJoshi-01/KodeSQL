from django.db import models


class SiteSettings(models.Model):
    """
    Global site settings.
    """
    site_name = models.CharField(max_length=255, default="SQL Playground")
    site_description = models.TextField(default="Interactive SQL learning platform")
    maintenance_mode = models.BooleanField(default=False)
    allow_registration = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("Only one SiteSettings instance is allowed")
        super().save(*args, **kwargs)
