from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from PIL import Image
import os
import uuid
from datetime import timedelta


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

    def get_display_name(self):
        """Get the user's display name (first name or username)"""
        return self.first_name if self.first_name else self.username

    def get_full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username


def user_profile_picture_path(instance, filename):
    """Generate upload path for user profile pictures"""
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('profile_pictures', filename)


class UserProfile(models.Model):
    """
    Extended user profile with additional settings and XP tracking.
    """
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Upload a profile picture (JPG, PNG, WebP - max 5MB)"
    )
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    total_xp = models.PositiveIntegerField(default=0, help_text="Cached total XP for performance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"

    def update_total_xp(self):
        """
        Update the cached total XP from all completed challenges.
        """
        from challenges.models import UserChallengeProgress
        total = UserChallengeProgress.objects.filter(
            user=self.user,
            is_completed=True
        ).aggregate(total=models.Sum('xp_earned'))['total'] or 0

        self.total_xp = total
        self.save(update_fields=['total_xp', 'updated_at'])
        return total

    def get_profile_picture_url(self):
        """Get profile picture URL or default avatar"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None

    def get_avatar_url(self):
        """Get avatar URL (profile picture or default)"""
        profile_url = self.get_profile_picture_url()
        if profile_url:
            return profile_url
        # Return a default avatar URL or None for CSS fallback
        return None

    def save(self, *args, **kwargs):
        """Override save to handle image processing"""
        # Delete old profile picture if updating
        if self.pk:
            try:
                old_profile = UserProfile.objects.get(pk=self.pk)
                if old_profile.profile_picture and old_profile.profile_picture != self.profile_picture:
                    if os.path.isfile(old_profile.profile_picture.path):
                        os.remove(old_profile.profile_picture.path)
            except UserProfile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Process uploaded image
        if self.profile_picture:
            self._process_profile_picture()

    def _process_profile_picture(self):
        """Process and resize profile picture"""
        try:
            img = Image.open(self.profile_picture.path)

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Resize to 300x300 (square)
            size = (300, 300)
            img = img.resize(size, Image.Resampling.LANCZOS)

            # Save with optimization
            img.save(self.profile_picture.path, 'JPEG', quality=85, optimize=True)

        except Exception as e:
            print(f"Error processing profile picture: {e}")

    def delete(self, *args, **kwargs):
        """Override delete to clean up profile picture file"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)


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


class PasswordResetToken(models.Model):
    """
    Password reset tokens for user password reset.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
