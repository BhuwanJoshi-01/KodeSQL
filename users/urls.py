"""
URL configuration for users app.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('email-verification-pending/<int:user_id>/', views.email_verification_pending, name='email_verification_pending'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('profile/', views.profile_view, name='profile'),

    # OAuth error handling
    path('oauth-error/', views.oauth_error_handler, name='oauth_error'),
    path('check-email-conflict/', views.check_oauth_email_conflict, name='check_email_conflict'),
    path('link-social-account/', views.link_social_account, name='link_social_account'),
    path('unlink-social-account/<int:account_id>/', views.unlink_social_account, name='unlink_social_account'),
    path('profile/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('api/update-theme/', views.update_theme_api, name='update_theme_api'),
]
