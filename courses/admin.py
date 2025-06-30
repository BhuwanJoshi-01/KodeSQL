from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Course, CourseModule, CourseLesson, UserCourseEnrollment,
    CourseReview, CourseCertificate, CoursePayment
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
    list_display = ('title', 'module', 'lesson_type', 'duration_minutes', 'order', 'is_active', 'is_preview')
    list_filter = ('lesson_type', 'is_active', 'is_preview', 'module__course')
    search_fields = ('title', 'content', 'module__title', 'module__course__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('module__course', 'module__order', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'lesson_type', 'order')
        }),
        ('Content', {
            'fields': ('content', 'video_url', 'video_duration', 'attachments')
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
