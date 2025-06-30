from django.db import models
from django.conf import settings


class QueryHistory(models.Model):
    """
    Store user's query execution history.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='query_history')
    query = models.TextField()
    executed_at = models.DateTimeField(auto_now_add=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-executed_at']
        verbose_name_plural = "Query histories"

    def __str__(self):
        return f"{self.user.email} - {self.query[:50]}..."


class SavedQuery(models.Model):
    """
    Store user's saved queries.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_queries')
    title = models.CharField(max_length=255)
    query = models.TextField()
    description = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'title']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
