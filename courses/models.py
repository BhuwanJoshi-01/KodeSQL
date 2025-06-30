from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from decimal import Decimal


class Course(models.Model):
    """
    Main course model with support for paid courses.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    COURSE_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('premium', 'Premium'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = CKEditor5Field(config_name='tutorial')
    short_description = models.TextField(max_length=500, help_text="Brief description for course cards")
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='free')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    preview_video = models.URLField(blank=True, help_text="YouTube or Vimeo URL for course preview")

    # Course metadata
    duration_hours = models.PositiveIntegerField(default=0, help_text="Estimated course duration in hours")
    skill_level = models.CharField(max_length=50, blank=True, help_text="e.g., 'No prior experience needed'")
    language = models.CharField(max_length=50, default='English')

    # SEO and organization
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    category = models.CharField(max_length=100, blank=True)
    prerequisites = CKEditor5Field(config_name='tutorial', blank=True)
    learning_outcomes = CKEditor5Field(config_name='tutorial', blank=True)

    # Settings
    is_featured = models.BooleanField(default=False)
    allow_preview = models.BooleanField(default=True, help_text="Allow non-enrolled users to preview first module")
    certificate_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Instructor
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_taught')

    class Meta:
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['status', 'course_type']),
            models.Index(fields=['difficulty', 'category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_course_type_display()})"

    @property
    def module_count(self):
        return self.modules.count()

    @property
    def total_lessons(self):
        return sum(module.lesson_count for module in self.modules.all())

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status__in=['active', 'completed']).count()

    @property
    def average_rating(self):
        ratings = self.reviews.aggregate(avg_rating=models.Avg('rating'))
        return round(ratings['avg_rating'] or 0, 1)

    @property
    def effective_price(self):
        """Return the effective price (discount price if available, otherwise regular price)"""
        return self.discount_price if self.discount_price else self.price

    @property
    def is_free(self):
        return self.course_type == 'free' or self.effective_price == 0

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class CourseModule(models.Model):
    """
    Course modules/sections containing lessons.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_preview = models.BooleanField(default=False, help_text="Allow preview for non-enrolled users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def total_duration(self):
        """Calculate total duration of all lessons in this module"""
        return sum(lesson.duration_minutes for lesson in self.lessons.all())


class CourseLesson(models.Model):
    """
    Individual lessons within course modules.
    """
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text/Article'),
        ('interactive', 'Interactive Exercise'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = CKEditor5Field(config_name='tutorial')
    lesson_type = models.CharField(max_length=15, choices=LESSON_TYPE_CHOICES, default='text')

    # Media content
    video_url = models.URLField(blank=True, help_text="YouTube, Vimeo, or direct video URL")
    video_duration = models.PositiveIntegerField(default=0, help_text="Video duration in seconds")
    attachments = models.FileField(upload_to='courses/lessons/', blank=True, null=True)

    # SQL-specific content
    example_query = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    practice_query = models.TextField(blank=True, help_text="Query for students to practice")

    # Lesson metadata
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Estimated lesson duration in minutes")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_preview = models.BooleanField(default=False, help_text="Allow preview for non-enrolled users")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"


class UserCourseEnrollment(models.Model):
    """
    Track user enrollment in courses with payment support.
    """
    ENROLLMENT_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=15, choices=ENROLLMENT_STATUS_CHOICES, default='active')

    # Payment tracking
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True)

    # Progress tracking
    current_module = models.ForeignKey(CourseModule, on_delete=models.SET_NULL, null=True, blank=True)
    current_lesson = models.ForeignKey(CourseLesson, on_delete=models.SET_NULL, null=True, blank=True)
    completed_lessons = models.ManyToManyField(CourseLesson, blank=True, related_name='completed_by_users')

    # Completion tracking
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['-enrolled_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.status})"

    @property
    def progress_percentage(self):
        """Calculate completion percentage based on completed lessons."""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0
        completed_count = self.completed_lessons.count()
        return min(int((completed_count / total_lessons) * 100), 100)

    def update_progress(self):
        """Update completion percentage and status."""
        self.completion_percentage = self.progress_percentage

        # Check if course is completed
        if self.completion_percentage == 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.status = 'completed'

            # Issue certificate if enabled
            if self.course.certificate_enabled and not self.certificate_issued:
                self.certificate_issued = True
                self.certificate_issued_at = timezone.now()

        self.save()

    @property
    def is_active_enrollment(self):
        """Check if enrollment is active and not expired."""
        if self.status != 'active':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class CourseReview(models.Model):
    """
    Course reviews and ratings by users.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.rating}/5)"


class CourseCertificate(models.Model):
    """
    Course completion certificates.
    """
    enrollment = models.OneToOneField(UserCourseEnrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    # Certificate data
    student_name = models.CharField(max_length=255)
    course_title = models.CharField(max_length=255)
    completion_date = models.DateField()
    instructor_name = models.CharField(max_length=255)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.student_name}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            # Generate unique certificate ID
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"

        # Auto-populate certificate data
        if not self.student_name:
            self.student_name = f"{self.enrollment.user.first_name} {self.enrollment.user.last_name}".strip()
            if not self.student_name:
                self.student_name = self.enrollment.user.email

        if not self.course_title:
            self.course_title = self.enrollment.course.title

        if not self.completion_date:
            self.completion_date = self.enrollment.completed_at.date() if self.enrollment.completed_at else timezone.now().date()

        if not self.instructor_name:
            instructor = self.enrollment.course.instructor
            self.instructor_name = f"{instructor.first_name} {instructor.last_name}".strip()
            if not self.instructor_name:
                self.instructor_name = instructor.email

        super().save(*args, **kwargs)


class CoursePayment(models.Model):
    """
    Track course payments for paid courses.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('razorpay', 'Razorpay'),
        ('manual', 'Manual'),
    ]

    enrollment = models.ForeignKey(UserCourseEnrollment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Payment gateway data
    transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.enrollment.user.email} - {self.amount} {self.currency}"
