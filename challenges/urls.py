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
    path('api/execute/<int:challenge_id>/', views.execute_challenge_query, name='execute_challenge_query'),
    path('api/submit/<int:challenge_id>/', views.submit_challenge, name='submit_challenge'),

    # Subscription views
    path('subscription/', views.subscription_plans, name='subscription_plans'),
    path('subscription/checkout/<int:plan_id>/', views.subscription_checkout, name='subscription_checkout'),
    path('subscription/cancel/<int:subscription_id>/', views.cancel_pending_subscription, name='cancel_pending_subscription'),

    # Stripe payment views
    path('subscription/stripe-checkout/<int:subscription_id>/', views.create_stripe_checkout, name='create_stripe_checkout'),
    path('subscription/payment-success/<int:subscription_id>/', views.payment_success, name='payment_success'),
    path('subscription/payment-cancel/<int:subscription_id>/', views.payment_cancel, name='payment_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Admin views
    path('admin/', views.admin_challenges_list, name='admin_challenges_list'),
    path('admin/create/', views.admin_challenge_create, name='admin_challenge_create'),

    # Challenge Subscription Plan Admin views (superuser only)
    path('admin/subscription-plans/', views.admin_subscription_plans_list, name='admin_subscription_plans_list'),
    path('admin/subscription-plans/create/', views.admin_subscription_plan_create, name='admin_subscription_plan_create'),
    path('admin/subscription-plans/<int:plan_id>/', views.admin_subscription_plan_detail, name='admin_subscription_plan_detail'),
    path('admin/subscription-plans/<int:plan_id>/edit/', views.admin_subscription_plan_edit, name='admin_subscription_plan_edit'),
    path('admin/subscription-plans/<int:plan_id>/delete/', views.admin_subscription_plan_confirm_delete, name='admin_subscription_plan_confirm_delete'),
    path('admin/subscription-plans/<int:plan_id>/delete/confirm/', views.admin_subscription_plan_delete, name='admin_subscription_plan_delete'),

    # Challenge User Subscription Admin views (superuser only)
    path('admin/subscriptions/', views.admin_subscriptions_list, name='admin_subscriptions_list'),
    path('admin/subscriptions/create/', views.admin_subscription_create, name='admin_subscription_create'),
    path('admin/subscriptions/<int:subscription_id>/', views.admin_subscription_detail, name='admin_subscription_detail'),
    path('admin/subscriptions/<int:subscription_id>/edit/', views.admin_subscription_edit, name='admin_subscription_edit'),
    path('admin/subscriptions/<int:subscription_id>/cancel/', views.admin_subscription_cancel, name='admin_subscription_cancel'),
    path('admin/subscriptions/<int:subscription_id>/delete/', views.admin_subscription_confirm_delete, name='admin_subscription_confirm_delete'),
    path('admin/subscriptions/<int:subscription_id>/delete/confirm/', views.admin_subscription_delete, name='admin_subscription_delete'),

    path('admin/<int:challenge_id>/', views.admin_challenge_detail, name='admin_challenge_detail'),
    path('admin/<int:challenge_id>/edit/', views.admin_challenge_edit, name='admin_challenge_edit'),
    path('admin/<int:challenge_id>/delete/', views.admin_challenge_delete, name='admin_challenge_delete'),
]
