from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from decimal import Decimal
from datetime import timedelta
import uuid


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
    video_file = models.FileField(
        upload_to='courses/videos/',
        blank=True,
        null=True,
        help_text="Upload video file (MP4, WebM, AVI, MOV supported)"
    )
    video_duration = models.PositiveIntegerField(
        default=0,
        help_text="Video duration in seconds (auto-detected when possible)"
    )
    video_thumbnail = models.ImageField(
        upload_to='courses/video_thumbnails/',
        blank=True,
        null=True,
        help_text="Upload custom video thumbnail (auto-generated if not provided)"
    )
    video_size = models.PositiveIntegerField(
        default=0,
        help_text="Video file size in bytes"
    )
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

    @property
    def has_video(self):
        """Check if lesson has video content"""
        return bool(self.video_file)

    @property
    def video_source(self):
        """Get the video source URL"""
        if self.video_file:
            return self.video_file.url
        return None

    @property
    def formatted_video_size(self):
        """Return human-readable video file size"""
        if self.video_size == 0:
            return "Unknown size"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.video_size < 1024.0:
                return f"{self.video_size:.1f} {unit}"
            self.video_size /= 1024.0
        return f"{self.video_size:.1f} TB"

    @property
    def formatted_duration(self):
        """Return formatted duration string"""
        if self.duration_minutes == 0:
            return "No duration set"
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def save(self, *args, **kwargs):
        # Auto-set video file size
        if self.video_file and self.video_size == 0:
            self.video_size = self.video_file.size

        super().save(*args, **kwargs)


class LessonResource(models.Model):
    """
    Resources/materials attached to course lessons.
    """
    RESOURCE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('ppt', 'Presentation'),
        ('code', 'Code File'),
        ('dataset', 'Dataset'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]

    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='courses/resources/')
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    download_count = models.PositiveIntegerField(default=0)
    is_downloadable = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['lesson', 'order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def file_extension(self):
        """Get file extension"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ''

    @property
    def formatted_file_size(self):
        """Return human-readable file size"""
        if self.file_size == 0:
            return "Unknown size"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    def save(self, *args, **kwargs):
        # Auto-detect resource type based on file extension
        if self.file and not self.resource_type or self.resource_type == 'other':
            ext = self.file_extension
            if ext in ['pdf']:
                self.resource_type = 'pdf'
            elif ext in ['doc', 'docx']:
                self.resource_type = 'doc'
            elif ext in ['ppt', 'pptx']:
                self.resource_type = 'ppt'
            elif ext in ['py', 'js', 'html', 'css', 'sql', 'java', 'cpp', 'c']:
                self.resource_type = 'code'
            elif ext in ['csv', 'xlsx', 'json', 'xml']:
                self.resource_type = 'dataset'
            elif ext in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
                self.resource_type = 'image'

        # Set file size
        if self.file and self.file_size == 0:
            self.file_size = self.file.size

        super().save(*args, **kwargs)


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


class SubscriptionPlan(models.Model):
    """Subscription plans for courses"""
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('unlimited', 'Unlimited'),
    ]

    PLAN_TYPE_CHOICES = [
        ('global', 'Global (All Courses)'),
        ('course_specific', 'Course Specific'),
    ]

    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    features = models.JSONField(default=list, help_text="List of features for this plan")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='course_specific')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True,
                              help_text="Leave blank for global plans")
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']
        unique_together = ['course', 'duration', 'plan_type']

    def __str__(self):
        course_name = self.course.title if self.course else "All Courses"
        return f"{self.name} - {course_name} ({self.get_duration_display()})"

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
            'unlimited': None,
        }
        return duration_map.get(self.duration)


class UserSubscription(models.Model):
    """User subscriptions to courses"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    enrollment = models.ForeignKey(UserCourseEnrollment, on_delete=models.CASCADE,
                                 related_name='subscriptions', null=True, blank=True)

    # Subscription details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)  # Null for unlimited plans
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Payment tracking
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)

    # Notifications
    expiry_notification_sent = models.BooleanField(default=False)
    final_notification_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'course', 'plan']

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.plan.name})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False

        if self.end_date is None:  # Unlimited plan
            return True

        return timezone.now() <= self.end_date

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

        # Activate enrollment if exists
        if self.enrollment:
            self.enrollment.status = 'active'
            self.enrollment.save()

    def expire(self):
        """Expire the subscription"""
        self.status = 'expired'
        self.save()

        # Deactivate enrollment if exists
        if self.enrollment:
            self.enrollment.status = 'expired'
            self.enrollment.save()
