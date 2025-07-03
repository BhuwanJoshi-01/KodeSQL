from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Course, CourseModule, CourseLesson, LessonResource, UserCourseEnrollment,
    CourseReview, CourseCertificate, CoursePayment, SubscriptionPlan, UserSubscription
)


# Import/Export Resources
class CourseResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'difficulty', 'course_type', 'price', 'status', 'instructor__email')


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0
    fields = ('title', 'order', 'is_active', 'is_preview')
    ordering = ('order',)


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0
    fields = ('title', 'lesson_type', 'duration_minutes', 'order', 'is_active', 'is_preview')
    ordering = ('order',)


class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0
    fields = ('title', 'file', 'resource_type', 'is_downloadable', 'order')
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource
    list_display = ('title', 'course_type', 'difficulty', 'price', 'status', 'enrolled_count_display', 'instructor', 'created_at')
    list_filter = ('course_type', 'difficulty', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'tags', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'enrolled_count_display', 'average_rating_display')
    inlines = [CourseModuleInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'instructor')
        }),
        ('Course Settings', {
            'fields': ('difficulty', 'course_type', 'status', 'category', 'language', 'tags')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('thumbnail', 'preview_video'),
            'classes': ('collapse',)
        }),
        ('Course Content', {
            'fields': ('duration_hours', 'skill_level', 'prerequisites', 'learning_outcomes'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'allow_preview', 'certificate_enabled', 'order'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('enrolled_count_display', 'average_rating_display'),
            'classes': ('collapse',)
        }),
    )

    def enrolled_count_display(self, obj):
        count = obj.enrolled_count
        if count > 0:
            url = reverse('admin:courses_usercourseenrollment_changelist') + f'?course__id__exact={obj.id}'
            return format_html('<a href="{}">{} students</a>', url, count)
        return '0 students'
    enrolled_count_display.short_description = 'Enrolled Students'

    def average_rating_display(self, obj):
        rating = obj.average_rating
        if rating > 0:
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html('{} ({}/5)', stars, rating)
        return 'No ratings'
    average_rating_display.short_description = 'Average Rating'


# Subscription Plan Resources
class SubscriptionPlanResource(resources.ModelResource):
    class Meta:
        model = SubscriptionPlan
        fields = ('id', 'name', 'duration', 'price', 'original_price', 'plan_type', 'course__title', 'is_active', 'is_recommended')


class UserSubscriptionResource(resources.ModelResource):
    class Meta:
        model = UserSubscription
        fields = ('id', 'user__email', 'course__title', 'plan__name', 'status', 'start_date', 'end_date', 'amount_paid')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('instructor')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'lesson_count_display', 'is_active', 'is_preview')
    list_filter = ('course', 'is_active', 'is_preview')
    search_fields = ('title', 'description', 'course__title')
    inlines = [CourseLessonInline]
    ordering = ('course', 'order')

    def lesson_count_display(self, obj):
        count = obj.lesson_count
        if count > 0:
            url = reverse('admin:courses_courselesson_changelist') + f'?module__id__exact={obj.id}'
            return format_html('<a href="{}">{} lessons</a>', url, count)
        return '0 lessons'
    lesson_count_display.short_description = 'Lessons'


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'lesson_type', 'has_video_display', 'resource_count_display', 'duration_minutes', 'order', 'is_active', 'is_preview')
    list_filter = ('lesson_type', 'is_active', 'is_preview', 'module__course')
    search_fields = ('title', 'content', 'module__title', 'module__course__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('module__course', 'module__order', 'order')
    inlines = [LessonResourceInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'lesson_type', 'order')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Video Content', {
            'fields': ('video_url', 'video_file', 'video_duration', 'video_thumbnail'),
            'classes': ('collapse',)
        }),
        ('Legacy Attachments', {
            'fields': ('attachments',),
            'classes': ('collapse',),
            'description': 'Use the Resources section below for new file uploads'
        }),
        ('SQL Content', {
            'fields': ('example_query', 'expected_output', 'practice_query'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('duration_minutes', 'is_active', 'is_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_video_display(self, obj):
        if obj.has_video:
            if obj.video_file:
                return format_html('<span style="color: green;">✓ File</span>')
            else:
                return format_html('<span style="color: blue;">✓ URL</span>')
        return format_html('<span style="color: gray;">✗ No video</span>')
    has_video_display.short_description = 'Video'

    def resource_count_display(self, obj):
        count = obj.resources.count()
        if count > 0:
            url = reverse('admin:courses_lessonresource_changelist') + f'?lesson__id__exact={obj.id}'
            return format_html('<a href="{}">{} resources</a>', url, count)
        return '0 resources'
    resource_count_display.short_description = 'Resources'


@admin.register(UserCourseEnrollment)
class UserCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'course_title', 'status', 'completion_percentage', 'amount_paid', 'enrolled_at')
    list_filter = ('status', 'is_completed', 'certificate_issued', 'course__course_type', 'enrolled_at')
    search_fields = ('user__email', 'course__title', 'payment_reference')
    readonly_fields = ('enrolled_at', 'completed_at', 'last_accessed', 'progress_percentage_display')
    raw_id_fields = ('user', 'course', 'current_module', 'current_lesson')
    filter_horizontal = ('completed_lessons',)

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('user', 'course', 'status', 'enrolled_at')
        }),
        ('Payment Information', {
            'fields': ('amount_paid', 'payment_method', 'payment_reference'),
            'classes': ('collapse',)
        }),
        ('Progress Tracking', {
            'fields': ('current_module', 'current_lesson', 'completed_lessons', 'progress_percentage_display')
        }),
        ('Completion', {
            'fields': ('is_completed', 'completion_percentage', 'completed_at', 'certificate_issued', 'certificate_issued_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_accessed', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def course_title(self, obj):
        return obj.course.title
    course_title.short_description = 'Course'
    course_title.admin_order_field = 'course__title'

    def progress_percentage_display(self, obj):
        percentage = obj.progress_percentage
        if percentage == 100:
            return format_html('<span style="color: green;">{}% ✓</span>', percentage)
        elif percentage > 0:
            return format_html('<span style="color: orange;">{}%</span>', percentage)
        else:
            return format_html('<span style="color: gray;">{}%</span>', percentage)
    progress_percentage_display.short_description = 'Progress'

    actions = ['mark_completed', 'issue_certificates']

    def mark_completed(self, request, queryset):
        for enrollment in queryset:
            enrollment.update_progress()
        self.message_user(request, f"Updated progress for {queryset.count()} enrollments.")
    mark_completed.short_description = "Update progress for selected enrollments"

    def issue_certificates(self, request, queryset):
        count = 0
        for enrollment in queryset.filter(is_completed=True, certificate_issued=False):
            if enrollment.course.certificate_enabled:
                enrollment.certificate_issued = True
                enrollment.certificate_issued_at = timezone.now()
                enrollment.save()
                count += 1
        self.message_user(request, f"Issued certificates for {count} completed enrollments.")
    issue_certificates.short_description = "Issue certificates for completed enrollments"


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'course_title', 'rating', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('user__email', 'course__title', 'review_text')
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def course_title(self, obj):
        return obj.course.title
    course_title.short_description = 'Course'
    course_title.admin_order_field = 'course__title'

    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"Approved {queryset.count()} reviews.")
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"Disapproved {queryset.count()} reviews.")
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student_name', 'course_title', 'completion_date', 'is_valid', 'issued_at')
    list_filter = ('is_valid', 'issued_at', 'completion_date')
    search_fields = ('certificate_id', 'student_name', 'course_title', 'enrollment__user__email')
    readonly_fields = ('certificate_id', 'issued_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing certificate
            return self.readonly_fields + ('enrollment',)
        return self.readonly_fields


@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'course_title', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'currency', 'created_at')
    search_fields = ('enrollment__user__email', 'enrollment__course__title', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    def user_email(self, obj):
        return obj.enrollment.user.email
    user_email.short_description = 'User'

    def course_title(self, obj):
        return obj.enrollment.course.title
    course_title.short_description = 'Course'

    fieldsets = (
        ('Payment Information', {
            'fields': ('enrollment', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_display', 'duration', 'price', 'is_active', 'is_recommended', 'sort_order')
    list_filter = ('duration', 'plan_type', 'is_active', 'is_recommended', 'course')
    search_fields = ('name', 'description', 'course__title')
    list_editable = ('is_active', 'is_recommended', 'sort_order')
    ordering = ('sort_order', 'course', 'duration')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'duration', 'plan_type', 'course')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Content', {
            'fields': ('description', 'features')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_recommended', 'sort_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def course_display(self, obj):
        if obj.course:
            return obj.course.title
        return "All Courses"
    course_display.short_description = 'Course'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'course_title', 'plan_name', 'status', 'start_date', 'end_date', 'time_remaining_display')
    list_filter = ('status', 'plan__duration', 'start_date', 'end_date')
    search_fields = ('user__email', 'course__title', 'plan__name')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)

    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'course', 'plan', 'enrollment')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Payment', {
            'fields': ('amount_paid', 'payment_reference')
        }),
        ('Notifications', {
            'fields': ('expiry_notification_sent', 'final_notification_sent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    def course_title(self, obj):
        return obj.course.title
    course_title.short_description = 'Course'

    def plan_name(self, obj):
        return obj.plan.name
    plan_name.short_description = 'Plan'

    def time_remaining_display(self, obj):
        if obj.status == 'active' and obj.end_date:
            from django.utils import timezone
            remaining = obj.end_date - timezone.now().date()
            if remaining.days > 0:
                return f"{remaining.days} days"
            elif remaining.days == 0:
                return "Expires today"
            else:
                return "Expired"
        return "N/A"
    time_remaining_display.short_description = 'Time Remaining'


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'resource_type', 'formatted_file_size_display', 'download_count', 'is_downloadable', 'order')
    list_filter = ('resource_type', 'is_downloadable', 'lesson__module__course')
    search_fields = ('title', 'description', 'lesson__title', 'lesson__module__title', 'lesson__module__course__title')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'download_count', 'file_extension_display')
    ordering = ('lesson__module__course', 'lesson__module__order', 'lesson__order', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'title', 'description', 'order')
        }),
        ('File Information', {
            'fields': ('file', 'resource_type', 'file_extension_display', 'file_size', 'formatted_file_size_display')
        }),
        ('Settings', {
            'fields': ('is_downloadable', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formatted_file_size_display(self, obj):
        return obj.formatted_file_size
    formatted_file_size_display.short_description = 'File Size'

    def file_extension_display(self, obj):
        ext = obj.file_extension
        if ext:
            return format_html('<span style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace;">.{}</span>', ext)
        return 'No extension'
    file_extension_display.short_description = 'File Type'

    def time_remaining_display(self, obj):
        if obj.end_date is None:
            return "Unlimited"

        if obj.status != 'active':
            return f"Status: {obj.get_status_display()}"

        remaining = obj.end_date - timezone.now()
        if remaining.days > 0:
            return f"{remaining.days} days"
        elif remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} hours"
        else:
            return "Expires soon"
    time_remaining_display.short_description = 'Time Remaining'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'plan', 'enrollment')

    actions = ['activate_subscriptions', 'expire_subscriptions']

    def activate_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.activate()
        self.message_user(request, f"Activated {queryset.count()} subscriptions.")
    activate_subscriptions.short_description = "Activate selected subscriptions"

    def expire_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.expire()
        self.message_user(request, f"Expired {queryset.count()} subscriptions.")
    expire_subscriptions.short_description = "Expire selected subscriptions"
