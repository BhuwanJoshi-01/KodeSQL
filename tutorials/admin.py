from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Tutorial, Lesson, UserTutorialProgress


# Import/Export Resources
class TutorialResource(resources.ModelResource):
    class Meta:
        model = Tutorial
        fields = ('id', 'title', 'description', 'difficulty', 'icon', 'is_active', 'order')


class LessonResource(resources.ModelResource):
    class Meta:
        model = Lesson
        fields = ('id', 'tutorial__title', 'title', 'content', 'example_query', 'expected_output', 'video_url', 'order', 'is_active')


class LessonInline(admin.StackedInline):
    """
    Inline admin for Lesson model within Tutorial admin.
    """
    model = Lesson
    extra = 0
    fields = ['title', 'content', 'example_query', 'expected_output', 'video_url', 'attachments', 'order', 'is_active']
    ordering = ['order']
    classes = ['collapse']


@admin.register(Tutorial)
class TutorialAdmin(ImportExportModelAdmin):
    """
    Enhanced admin interface for Tutorial model with import/export.
    """
    resource_class = TutorialResource
    list_display = ['title', 'difficulty', 'lesson_count', 'thumbnail_preview', 'is_active', 'order', 'created_at']
    list_filter = ['difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order', 'difficulty', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'lesson_count', 'thumbnail_preview']
    inlines = [LessonInline]
    list_editable = ['is_active', 'order']
    actions = ['make_active', 'make_inactive', 'duplicate_tutorial']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'difficulty', 'icon', 'order', 'is_active')
        }),
        ('Media', {
            'fields': ('thumbnail', 'thumbnail_preview'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('lesson_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} tutorials marked as active.")
    make_active.short_description = "Mark selected tutorials as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} tutorials marked as inactive.")
    make_inactive.short_description = "Mark selected tutorials as inactive"

    def duplicate_tutorial(self, request, queryset):
        for tutorial in queryset:
            tutorial.pk = None
            tutorial.title = f"{tutorial.title} (Copy)"
            tutorial.save()
        self.message_user(request, f"{queryset.count()} tutorials duplicated.")
    duplicate_tutorial.short_description = "Duplicate selected tutorials"


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    """
    Enhanced admin interface for Lesson model.
    """
    resource_class = LessonResource
    list_display = ['tutorial', 'title', 'order', 'has_video', 'has_attachments', 'is_active', 'created_at']
    list_filter = ['tutorial', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'tutorial__title']
    ordering = ['tutorial', 'order', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['order', 'is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('tutorial', 'title', 'order', 'is_active')
        }),
        ('Content', {
            'fields': ('content', 'example_query', 'expected_output')
        }),
        ('Media', {
            'fields': ('video_url', 'attachments'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = "Has Video"

    def has_attachments(self, obj):
        return bool(obj.attachments)
    has_attachments.boolean = True
    has_attachments.short_description = "Has Attachments"


@admin.register(UserTutorialProgress)
class UserTutorialProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for UserTutorialProgress model.
    """
    list_display = ['user', 'tutorial', 'progress_percentage', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'tutorial__difficulty', 'started_at']
    search_fields = ['user__email', 'tutorial__title']
    ordering = ['-updated_at']
    readonly_fields = ['started_at', 'updated_at', 'progress_percentage']
