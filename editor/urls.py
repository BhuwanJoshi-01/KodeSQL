"""
URL configuration for editor app.
"""

from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.sql_editor, name='sql_editor'),
    path('api/execute/', views.execute_query, name='execute_query'),
    path('api/history/', views.query_history, name='query_history'),
    path('api/saved-queries/', views.saved_queries, name='saved_queries'),
    path('api/save-query/', views.save_query, name='save_query'),
    path('api/delete-query/<int:query_id>/', views.delete_saved_query, name='delete_saved_query'),
    path('api/export/<str:format>/', views.export_results, name='export_results'),
]
