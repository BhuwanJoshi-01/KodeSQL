"""
URL configuration for tutorials app.
"""

from django.urls import path
from . import views

app_name = 'tutorials'

urlpatterns = [
    # Public views
    path('', views.tutorials_list, name='tutorials_list'),
    path('<int:tutorial_id>/', views.tutorial_detail, name='tutorial_detail'),
    path('<int:tutorial_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('api/complete-lesson/', views.complete_lesson, name='complete_lesson'),

    # Admin views
    path('admin/', views.admin_tutorials_list, name='admin_tutorials_list'),
    path('admin/create/', views.admin_tutorial_create, name='admin_tutorial_create'),
    path('admin/<int:tutorial_id>/', views.admin_tutorial_detail, name='admin_tutorial_detail'),
    path('admin/<int:tutorial_id>/edit/', views.admin_tutorial_edit, name='admin_tutorial_edit'),
    path('admin/<int:tutorial_id>/delete/', views.admin_tutorial_delete, name='admin_tutorial_delete'),
    path('admin/<int:tutorial_id>/lesson/create/', views.admin_lesson_create, name='admin_lesson_create'),
    path('admin/lesson/<int:lesson_id>/edit/', views.admin_lesson_edit, name='admin_lesson_edit'),
    path('admin/lesson/<int:lesson_id>/delete/', views.admin_lesson_delete, name='admin_lesson_delete'),
]
