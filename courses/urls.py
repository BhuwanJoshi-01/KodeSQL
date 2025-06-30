from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Public course views
    path('', views.courses_list, name='courses_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),

    # User course management
    path('my-courses/', views.my_courses, name='my_courses'),
    path('certificates/<str:certificate_id>/', views.certificate_view, name='certificate_view'),

    # API endpoints
    path('api/my-courses/', views.api_my_courses, name='api_my_courses'),
    path('api/courses/', views.api_courses_list, name='api_courses_list'),
    path('api/enroll/<slug:slug>/', views.api_course_enroll, name='api_course_enroll'),
    path('api/lesson-complete/<int:lesson_id>/', views.api_lesson_complete, name='api_lesson_complete'),

    # Admin views (staff only)
    path('admin/', views.admin_courses_list, name='admin_courses_list'),
    path('admin/create/', views.admin_course_create, name='admin_course_create'),
    path('admin/<slug:slug>/', views.admin_course_detail, name='admin_course_detail'),
    path('admin/<slug:slug>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/<slug:slug>/delete/', views.admin_course_delete, name='admin_course_delete'),
]
