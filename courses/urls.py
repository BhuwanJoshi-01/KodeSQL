from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Admin views (staff only) - Must come before slug patterns
    path('admin/', views.admin_courses_list, name='admin_courses_list'),
    path('admin/create/', views.admin_course_create, name='admin_course_create'),

    # Subscription Plan Admin views (staff only)
    path('admin/subscription-plans/', views.admin_subscription_plans_list, name='admin_subscription_plans_list'),
    path('admin/subscription-plans/create/', views.admin_subscription_plan_create, name='admin_subscription_plan_create'),
    path('admin/subscription-plans/<int:plan_id>/', views.admin_subscription_plan_detail, name='admin_subscription_plan_detail'),
    path('admin/subscription-plans/<int:plan_id>/edit/', views.admin_subscription_plan_edit, name='admin_subscription_plan_edit'),
    path('admin/subscription-plans/<int:plan_id>/delete/', views.admin_subscription_plan_confirm_delete, name='admin_subscription_plan_confirm_delete'),
    path('admin/subscription-plans/<int:plan_id>/delete/confirm/', views.admin_subscription_plan_delete, name='admin_subscription_plan_delete'),

    path('admin/<slug:slug>/', views.admin_course_detail, name='admin_course_detail'),
    path('admin/<slug:slug>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/<slug:slug>/delete/', views.admin_course_delete, name='admin_course_delete'),

    # Enhanced admin content management
    path('admin/<slug:course_slug>/modules/create/', views.admin_module_create, name='admin_module_create'),
    path('admin/<slug:course_slug>/modules/<int:module_id>/edit/', views.admin_module_edit, name='admin_module_edit'),
    path('admin/<slug:course_slug>/modules/<int:module_id>/delete/', views.admin_module_delete, name='admin_module_delete'),

    path('admin/<slug:course_slug>/modules/<int:module_id>/lessons/create/', views.admin_lesson_create, name='admin_lesson_create'),
    path('admin/<slug:course_slug>/lessons/<int:lesson_id>/edit/', views.admin_lesson_edit, name='admin_lesson_edit'),
    path('admin/<slug:course_slug>/lessons/<int:lesson_id>/delete/', views.admin_lesson_delete, name='admin_lesson_delete'),
    path('admin/<slug:course_slug>/lessons/<int:lesson_id>/resources/', views.admin_lesson_resources, name='admin_lesson_resources'),

    path('admin/<slug:course_slug>/resources/<int:resource_id>/edit/', views.admin_resource_edit, name='admin_resource_edit'),
    path('admin/<slug:course_slug>/resources/<int:resource_id>/delete/', views.admin_resource_delete, name='admin_resource_delete'),

    path('admin/<slug:course_slug>/structure/reorder/', views.admin_course_structure_reorder, name='admin_course_structure_reorder'),
    path('admin/<slug:course_slug>/preview/', views.admin_course_preview, name='admin_course_preview'),

    # User course management
    path('my-courses/', views.my_courses, name='my_courses'),
    path('certificates/<str:certificate_id>/', views.certificate_view, name='certificate_view'),

    # Course watching
    path('<slug:slug>/watch/', views.course_watch, name='course_watch'),
    path('<slug:slug>/watch/module/<int:module_id>/', views.course_watch, name='course_watch_module'),
    path('<slug:slug>/watch/lesson/<int:lesson_id>/', views.course_watch, name='course_watch_lesson'),

    # Resource downloads
    path('resource/download/<int:resource_id>/', views.download_lesson_resource, name='download_lesson_resource'),

    # Payment views
    path('payment/<int:payment_id>/', views.payment_page, name='payment_page'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),

    # API endpoints
    path('api/my-courses/', views.api_my_courses, name='api_my_courses'),
    path('api/courses/', views.api_courses_list, name='api_courses_list'),
    path('api/enroll/<slug:slug>/', views.api_course_enroll, name='api_course_enroll'),
    path('api/lesson-complete/<int:lesson_id>/', views.api_lesson_complete, name='api_lesson_complete'),

    # Public course views - Must come after specific patterns
    path('', views.courses_list, name='courses_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),

    # Subscription plans
    path('<slug:slug>/plans/', views.subscription_plans, name='subscription_plans'),
    path('<slug:course_slug>/checkout/<int:plan_id>/', views.subscription_checkout, name='subscription_checkout'),
]
