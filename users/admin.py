from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserDatabase, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    """
    list_display = ['email', 'username', 'is_email_verified', 'is_active', 'date_joined']
    list_filter = ['is_email_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Email Verification', {'fields': ('is_email_verified',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    """
    list_display = ['user', 'theme_preference', 'created_at']
    list_filter = ['theme_preference', 'created_at']
    search_fields = ['user__email', 'user__username']
    ordering = ['-created_at']


@admin.register(UserDatabase)
class UserDatabaseAdmin(admin.ModelAdmin):
    """
    Admin interface for UserDatabase model.
    """
    list_display = ['user', 'database_path', 'created_at', 'last_accessed']
    list_filter = ['created_at', 'last_accessed']
    search_fields = ['user__email', 'user__username']
    ordering = ['-last_accessed']
    readonly_fields = ['database_path', 'full_path']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for EmailVerificationToken model.
    """
    list_display = ['user', 'token', 'created_at', 'expires_at', 'is_used', 'is_valid']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['token', 'created_at', 'is_expired', 'is_valid']
