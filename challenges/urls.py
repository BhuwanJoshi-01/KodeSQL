"""
URL configuration for challenges app.
"""

from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    # Public views
    path('', views.challenges_list, name='challenges_list'),
    path('<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('api/submit/<int:challenge_id>/', views.submit_challenge, name='submit_challenge'),

    # Admin views
    path('admin/', views.admin_challenges_list, name='admin_challenges_list'),
    path('admin/create/', views.admin_challenge_create, name='admin_challenge_create'),
    path('admin/<int:challenge_id>/', views.admin_challenge_detail, name='admin_challenge_detail'),
    path('admin/<int:challenge_id>/edit/', views.admin_challenge_edit, name='admin_challenge_edit'),
    path('admin/<int:challenge_id>/delete/', views.admin_challenge_delete, name='admin_challenge_delete'),
]
