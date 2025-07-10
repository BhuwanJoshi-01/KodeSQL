"""
Signal handlers for user authentication.
"""

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import UserProfile, UserDatabase

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile and database when a new user is created.
    Also automatically verify email for superusers and staff.
    """
    if created and instance.id:  # Ensure user has an ID before creating related objects
        try:
            UserProfile.objects.get_or_create(user=instance)
            UserDatabase.objects.get_or_create(user=instance)

            # Automatically verify email for superusers and staff
            if instance.is_superuser or instance.is_staff:
                instance.is_email_verified = True
                # Use update_fields to avoid triggering signals again
                instance.save(update_fields=['is_email_verified'])
        except Exception as e:
            print(f"❌ Error in create_user_profile signal: {e}")
            print(f"❌ User: {instance.email} (ID: {instance.id})")
