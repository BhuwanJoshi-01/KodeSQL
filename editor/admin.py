from django.contrib import admin
from .models import QueryHistory, SavedQuery


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for QueryHistory model.
    """
    list_display = ['user', 'query_preview', 'success', 'execution_time_ms', 'executed_at']
    list_filter = ['success', 'executed_at']
    search_fields = ['user__email', 'query']
    ordering = ['-executed_at']
    readonly_fields = ['executed_at']

    def query_preview(self, obj):
        """Show first 50 characters of query."""
        return obj.query[:50] + "..." if len(obj.query) > 50 else obj.query
    query_preview.short_description = "Query Preview"


@admin.register(SavedQuery)
class SavedQueryAdmin(admin.ModelAdmin):
    """
    Admin interface for SavedQuery model.
    """
    list_display = ['user', 'title', 'is_favorite', 'created_at', 'updated_at']
    list_filter = ['is_favorite', 'created_at', 'updated_at']
    search_fields = ['user__email', 'title', 'query']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
