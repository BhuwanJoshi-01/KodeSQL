from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from datetime import timedelta
import json


class Challenge(models.Model):
    """
    SQL challenges for users to solve.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('extreme', 'Extreme Hard'),
    ]

    SUBSCRIPTION_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    title = models.CharField(max_length=255)
    description = CKEditor5Field(config_name='tutorial')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    question = CKEditor5Field(config_name='tutorial')
    hint = CKEditor5Field(config_name='tutorial', blank=True)
    expected_query = models.TextField()
    expected_result = models.JSONField(default=list)  # Store expected result as JSON
    sample_data = models.FileField(upload_to='challenges/sample_data/', blank=True, null=True,
                                   help_text="Upload CSV or SQL file with sample data")

    # Subscription and categorization fields
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_TYPE_CHOICES, default='free')
    company = models.CharField(max_length=100, blank=True, help_text="Company associated with this challenge")
    tags = models.JSONField(default=list, help_text="List of tags for categorization (e.g., ['joins', 'aggregation'])")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'difficulty', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty})"

    @property
    def expected_result_json(self):
        """Return expected result as formatted JSON string."""
        return json.dumps(self.expected_result, indent=2)

    def user_has_access(self, user):
        """Check if user has access to this challenge"""
        # Free challenges are accessible to everyone
        if self.subscription_type == 'free':
            return True

        # Paid challenges require active subscription
        if not user or not user.is_authenticated:
            return False

        # Check if user has active challenge subscription
        active_subscription = UserChallengeSubscription.objects.filter(
            user=user,
            status='active'
        ).first()

        return active_subscription and active_subscription.is_active

    @property
    def is_premium(self):
        """Check if this is a premium challenge"""
        return self.subscription_type == 'paid'


class UserChallengeProgress(models.Model):
    """
    Track user progress on challenges.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_progress')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    best_query = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'challenge']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.email} - {self.challenge.title} ({status})"


class ChallengeSubscriptionPlan(models.Model):
    """Subscription plans for challenges"""
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('unlimited', 'Unlimited'),
    ]

    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    features = models.JSONField(default=list, help_text="List of features for this plan")
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']
        unique_together = ['duration']

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"

    @property
    def effective_price(self):
        """Return the effective price (discounted if available)"""
        return self.price

    @property
    def has_discount(self):
        """Check if plan has a discount"""
        return self.original_price and self.original_price > self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def get_duration_days(self):
        """Get duration in days"""
        duration_map = {
            '1_month': 30,
            '3_months': 90,
            '6_months': 180,
            'unlimited': None,
        }
        return duration_map.get(self.duration)


class UserChallengeSubscription(models.Model):
    """User subscriptions to challenges"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_subscriptions')
    plan = models.ForeignKey(ChallengeSubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')

    # Subscription details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)  # Null for unlimited plans
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Payment tracking
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)

    # Pending payment expiration
    pending_expires_at = models.DateTimeField(null=True, blank=True, help_text="When pending payment expires")

    # Notifications
    expiry_notification_sent = models.BooleanField(default=False)
    final_notification_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - Challenge Subscription ({self.plan.name})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False

        if self.end_date is None:  # Unlimited plan
            return True

        return timezone.now() <= self.end_date

    @property
    def is_pending_expired(self):
        """Check if pending payment has expired"""
        if self.status != 'pending':
            return False

        if self.pending_expires_at is None:
            return False

        return timezone.now() > self.pending_expires_at

    @property
    def is_expiring_soon(self):
        """Check if subscription expires within 7 days"""
        if self.end_date is None:
            return False

        days_until_expiry = (self.end_date - timezone.now()).days
        return 0 <= days_until_expiry <= 7

    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.end_date is None:
            return None

        days = (self.end_date - timezone.now()).days
        return max(0, days)

    @property
    def time_remaining(self):
        """Get human-readable time remaining"""
        if self.end_date is None:
            return "Unlimited"

        remaining = self.end_date - timezone.now()
        if remaining.days > 0:
            return f"{remaining.days} days"
        elif remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} hours"
        else:
            return "Expires soon"

    def activate(self):
        """Activate the subscription"""
        self.status = 'active'
        self.start_date = timezone.now()

        # Set end date based on plan duration
        if self.plan.duration != 'unlimited':
            duration_days = self.plan.get_duration_days()
            self.end_date = self.start_date + timedelta(days=duration_days)

        self.save()

    def expire(self):
        """Expire the subscription"""
        self.status = 'expired'
        self.save()

    def cancel_pending(self):
        """Cancel a pending subscription"""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()

    def set_pending_expiration(self, minutes=30):
        """Set when pending payment expires"""
        self.pending_expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save()

    @classmethod
    def cleanup_expired_pending(cls):
        """Clean up expired pending subscriptions"""
        expired_pending = cls.objects.filter(
            status='pending',
            pending_expires_at__lt=timezone.now()
        )
        count = expired_pending.count()
        expired_pending.update(status='expired')
        return count
