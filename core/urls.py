"""
URL configuration for core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('editor/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contribute/', views.contribute, name='contribute'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    # Debug URLs (only for development)
    path('csrf-debug/', views.csrf_debug, name='csrf_debug'),
    path('csrf-test/', views.csrf_test_form, name='csrf_test'),
]
