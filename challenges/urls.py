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
    path('admin/<int:challenge_id>/', views.admin_challenge_detail, name='admin_challenge_detail'),
    path('admin/<int:challenge_id>/edit/', views.admin_challenge_edit, name='admin_challenge_edit'),
    path('admin/<int:challenge_id>/delete/', views.admin_challenge_delete, name='admin_challenge_delete'),
]
