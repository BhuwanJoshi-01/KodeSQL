from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
import json


class Challenge(models.Model):
    """
    SQL challenges for users to solve.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
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
