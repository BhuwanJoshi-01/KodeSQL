from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
import os
import uuid


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Extended user profile with additional settings.
    """
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"


class UserDatabase(models.Model):
    """
    Track user-specific SQLite database files.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='database')
    database_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Database"

    @property
    def full_path(self):
        """Get the full path to the user's database file."""
        return os.path.join(settings.USER_DATABASES_DIR, self.database_path)

    def save(self, *args, **kwargs):
        if not self.database_path:
            self.database_path = f"user_{self.user.id}.db"
        super().save(*args, **kwargs)


class EmailVerificationToken(models.Model):
    """
    Email verification tokens for user registration.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification token for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
