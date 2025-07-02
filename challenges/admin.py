from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import json
from .models import Challenge, UserChallengeProgress, ChallengeSubscriptionPlan, UserChallengeSubscription


# Import/Export Resources
class ChallengeResource(resources.ModelResource):
    class Meta:
        model = Challenge
        fields = ('id', 'title', 'description', 'difficulty', 'question', 'hint', 'expected_query', 'expected_result', 'subscription_type', 'company', 'tags', 'is_active', 'order')


@admin.register(Challenge)
class ChallengeAdmin(ImportExportModelAdmin):
    """
    Enhanced admin interface for Challenge model with import/export.
    """
    resource_class = ChallengeResource
    list_display = ['title', 'difficulty', 'subscription_type', 'company', 'has_sample_data', 'is_active', 'order', 'created_at']
    list_filter = ['difficulty', 'subscription_type', 'company', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'question', 'company']
    ordering = ['order', 'difficulty', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'expected_result_preview']
    list_editable = ['is_active', 'order', 'subscription_type']
    actions = ['make_active', 'make_inactive', 'make_free', 'make_paid', 'duplicate_challenge']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'difficulty', 'order', 'is_active')
        }),
        ('Subscription & Categorization', {
            'fields': ('subscription_type', 'company', 'tags'),
            'description': 'Configure subscription requirements and categorization for this challenge.'
        }),
        ('Challenge Content', {
            'fields': ('question', 'hint', 'expected_query')
        }),
        ('Expected Results', {
            'fields': ('expected_result', 'expected_result_preview'),
            'classes': ('collapse',)
        }),
        ('Sample Data', {
            'fields': ('sample_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def expected_result_preview(self, obj):
        if obj.expected_result:
            try:
                formatted_json = json.dumps(obj.expected_result, indent=2)
                return format_html('<pre style="background: #f8f8f8; padding: 10px; border-radius: 4px; max-height: 200px; overflow-y: auto;">{}</pre>', formatted_json)
            except:
                return str(obj.expected_result)
        return "No expected result"
    expected_result_preview.short_description = "Expected Result Preview"

    def has_sample_data(self, obj):
        return bool(obj.sample_data)
    has_sample_data.boolean = True
    has_sample_data.short_description = "Has Sample Data"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} challenges marked as active.")
    make_active.short_description = "Mark selected challenges as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} challenges marked as inactive.")
    make_inactive.short_description = "Mark selected challenges as inactive"

    def make_free(self, request, queryset):
        queryset.update(subscription_type='free')
        self.message_user(request, f"{queryset.count()} challenges marked as free.")
    make_free.short_description = "Mark selected challenges as free"

    def make_paid(self, request, queryset):
        queryset.update(subscription_type='paid')
        self.message_user(request, f"{queryset.count()} challenges marked as paid.")
    make_paid.short_description = "Mark selected challenges as paid"

    def duplicate_challenge(self, request, queryset):
        for challenge in queryset:
            challenge.pk = None
            challenge.title = f"{challenge.title} (Copy)"
            challenge.save()
        self.message_user(request, f"{queryset.count()} challenges duplicated.")
    duplicate_challenge.short_description = "Duplicate selected challenges"


@admin.register(UserChallengeProgress)
class UserChallengeProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for UserChallengeProgress model.
    """
    list_display = ['user', 'challenge', 'is_completed', 'attempts', 'completed_at']
    list_filter = ['is_completed', 'challenge__difficulty', 'completed_at']
    search_fields = ['user__email', 'challenge__title']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChallengeSubscriptionPlan)
class ChallengeSubscriptionPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for ChallengeSubscriptionPlan model.
    """
    list_display = ['name', 'duration', 'price', 'original_price', 'is_active', 'is_recommended', 'sort_order']
    list_filter = ['duration', 'is_active', 'is_recommended']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'price']
    list_editable = ['price', 'is_active', 'is_recommended', 'sort_order']

    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'duration', 'description', 'sort_order')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Features & Settings', {
            'fields': ('features', 'is_active', 'is_recommended')
        }),
    )


@admin.register(UserChallengeSubscription)
class UserChallengeSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for UserChallengeSubscription model.
    """
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'amount_paid', 'is_active_status']
    list_filter = ['status', 'plan__duration', 'start_date', 'end_date']
    search_fields = ['user__email', 'plan__name', 'payment_reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'is_active_status', 'days_remaining_display']

    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'is_active_status', 'days_remaining_display')
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

    def is_active_status(self, obj):
        return obj.is_active
    is_active_status.boolean = True
    is_active_status.short_description = "Currently Active"

    def days_remaining_display(self, obj):
        if obj.days_remaining is None:
            return "Unlimited"
        return f"{obj.days_remaining} days"
    days_remaining_display.short_description = "Days Remaining"
