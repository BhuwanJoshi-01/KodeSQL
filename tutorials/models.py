from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Tutorial(models.Model):
    """
    SQL tutorials/courses.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    description = CKEditor5Field(config_name='tutorial')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    icon = models.CharField(max_length=50, default='table_chart')  # Material icon name
    thumbnail = models.ImageField(upload_to='tutorials/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'difficulty', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty})"

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def completed_by_user_count(self):
        return self.user_progress.filter(is_completed=True).count()


class Lesson(models.Model):
    """
    Individual lessons within tutorials.
    """
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = CKEditor5Field(config_name='tutorial')  # Rich text content with uploads
    example_query = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="Optional video tutorial URL")
    attachments = models.FileField(upload_to='tutorials/attachments/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['tutorial', 'order']

    def __str__(self):
        return f"{self.tutorial.title} - {self.title}"


class UserTutorialProgress(models.Model):
    """
    Track user progress through tutorials.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutorial_progress')
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='user_progress')
    current_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_lessons = models.ManyToManyField(Lesson, blank=True, related_name='completed_by_users')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'tutorial']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.email} - {self.tutorial.title} ({status})"

    @property
    def progress_percentage(self):
        """Calculate completion percentage."""
        total_lessons = self.tutorial.lessons.count()
        if total_lessons == 0:
            return 0
        completed_count = self.completed_lessons.count()
        return int((completed_count / total_lessons) * 100)
