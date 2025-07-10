from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import json
from .models import Challenge, ChallengeTable, UserChallengeProgress, ChallengeSubscriptionPlan, UserChallengeSubscription, XPTransaction


# Import/Export Resources
class ChallengeResource(resources.ModelResource):
    class Meta:
        model = Challenge
        fields = ('id', 'title', 'description', 'difficulty', 'question', 'hint', 'expected_query', 'expected_result', 'subscription_type', 'company', 'tags', 'is_active', 'order')


class ChallengeTableInline(admin.StackedInline):
    """
    Enhanced inline admin for ChallengeTable model with prominent "Add Another Database" functionality.
    Uses StackedInline for better visibility of schema and dataset fields.
    """
    model = ChallengeTable
    extra = 1  # Show 1 empty form by default
    max_num = 15  # Allow up to 15 tables per challenge
    ordering = ['order', 'table_name']
    verbose_name = "Database Schema"
    verbose_name_plural = "🗄️ Database Schemas - Add Multiple Tables for Complex Challenges"

    fieldsets = (
        ('Table Information', {
            'fields': ('table_name', 'order'),
            'classes': ('wide',)
        }),
        ('Schema Definition', {
            'fields': ('schema_sql',),
            'description': 'Define the CREATE TABLE statement for this database table.',
            'classes': ('wide',)
        }),
        ('Run Dataset (Test Data)', {
            'fields': ('run_dataset_sql',),
            'description': 'INSERT statements for test data that users see when testing their queries.',
            'classes': ('wide',)
        }),
        ('Submit Dataset (Validation Data)', {
            'fields': ('submit_dataset_sql',),
            'description': 'INSERT statements for validation data used in final submission checking.',
            'classes': ('wide',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/challenge_table_inline.css',)
        }
        js = ('admin/js/challenge_table_inline.js',)


@admin.register(Challenge)
class ChallengeAdmin(ImportExportModelAdmin):
    """
    Enhanced admin interface for Challenge model with import/export and multi-table support.
    """
    resource_class = ChallengeResource
    list_display = ['title', 'difficulty', 'xp', 'subscription_type', 'company', 'table_count_display', 'has_sample_data', 'is_active', 'order', 'created_at']
    list_filter = ['difficulty', 'subscription_type', 'company', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'question', 'company']
    ordering = ['order', 'difficulty', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'expected_result_preview', 'table_count_display', 'generate_output_button']
    list_editable = ['is_active', 'subscription_type']
    actions = ['make_active', 'make_inactive', 'make_free', 'make_paid', 'duplicate_challenge', 'regenerate_expected_results']
    inlines = [ChallengeTableInline]

    fieldsets = (
        ('📝 Basic Challenge Information', {
            'fields': ('title', 'description', 'difficulty', 'is_active', 'order'),
            'classes': ('wide',)
        }),
        ('🎯 Challenge Content', {
            'fields': ('question', 'hint', 'reference_query'),
            'description': '<strong>Define your challenge:</strong><br>'
                          '• <strong>Question:</strong> What should users accomplish?<br>'
                          '• <strong>Hint:</strong> Help users understand the approach<br>'
                          '• <strong>Solution Query:</strong> The correct SQL solution (can use multiple tables with JOINs)',
            'classes': ('wide',)
        }),
        ('🗄️ Multi-Database System Status', {
            'fields': ('table_count_display',),
            'description': '<div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3;">'
                          '<strong>📊 How to Add Multiple Database Tables:</strong><br>'
                          '1️⃣ Scroll down to the <strong>"Database Schemas"</strong> section below<br>'
                          '2️⃣ Click the <strong>"Add another Database Schema"</strong> button<br>'
                          '3️⃣ Fill in table name, schema SQL, run dataset, and submit dataset<br>'
                          '4️⃣ Repeat for each table you want to add<br>'
                          '5️⃣ Click <strong>"Generate Output JSON"</strong> when done<br><br>'
                          '<strong>💡 Pro Tip:</strong> Add 2-3 related tables for realistic JOIN scenarios!'
                          '</div>',
            'classes': ('wide',)
        }),
        ('⚙️ Configuration', {
            'fields': ('subscription_type', 'company', 'tags', 'xp'),
            'description': 'Configure subscription requirements, categorization, and experience points.',
            'classes': ('wide',)
        }),
        ('🎯 Expected Results & Validation', {
            'fields': ('generate_output_button', 'expected_result_preview'),
            'description': '<strong>Important:</strong> After adding your database tables and reference query, '
                          'click "Generate Output JSON" to automatically create expected results for validation.',
            'classes': ('wide',)
        }),
        ('🔧 Advanced Settings', {
            'fields': ('expected_result',),
            'classes': ('collapse',),
            'description': 'Raw expected result data (auto-generated, usually no need to edit manually).'
        }),
        ('📜 Legacy Single-Table System', {
            'fields': ('schema_sql', 'run_dataset_sql', 'submit_dataset_sql'),
            'classes': ('collapse',),
            'description': '⚠️ Legacy fields for old single-table challenges. Use the multi-database system above for new challenges.'
        }),
        ('📚 Legacy Fields', {
            'fields': ('expected_query', 'sample_data', 'mysql_schema_file'),
            'classes': ('collapse',),
            'description': 'Legacy fields kept for backward compatibility.'
        }),
        ('🕒 Timestamps', {
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

    def table_count_display(self, obj):
        """Display the number of tables in this challenge with add button"""
        count = obj.get_table_count()
        if obj.has_multi_table_setup():
            status = format_html('<span style="color: green;">✅ {} table(s) configured</span>', count)
        elif count > 0:
            status = format_html('<span style="color: orange;">⚠️ {} legacy table(s)</span>', count)
        else:
            status = format_html('<span style="color: red;">❌ No tables configured</span>')

        # Add instructions
        instructions = format_html(
            '<br><small style="color: #666;">'
            '📋 <strong>To add tables:</strong> Scroll down to "Challenge Database Tables" section → '
            'Click "➕ Add Another Database Table"'
            '</small>'
        )

        return format_html('{}{}', status, instructions)
    table_count_display.short_description = "Database Tables Status"

    def generate_output_button(self, obj):
        """Display a button to generate expected output JSON"""
        if obj.pk and obj.reference_query:
            return format_html(
                '<button type="button" onclick="generateExpectedOutput({})" '
                'class="button" style="background: #417690; color: white; padding: 8px 16px; '
                'border: none; border-radius: 4px; cursor: pointer;">'
                '🔄 Generate Output JSON</button>'
                '<div id="generate-result-{}" style="margin-top: 10px;"></div>'
                '<script>'
                'function generateExpectedOutput(challengeId) {{'
                '    const resultDiv = document.getElementById("generate-result-" + challengeId);'
                '    resultDiv.innerHTML = "<em>Generating...</em>";'
                '    fetch("/admin/challenges/challenge/" + challengeId + "/generate-output/", {{'
                '        method: "POST",'
                '        headers: {{'
                '            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,'
                '            "Content-Type": "application/json"'
                '        }}'
                '    }})'
                '    .then(response => response.json())'
                '    .then(data => {{'
                '        if (data.success) {{'
                '            resultDiv.innerHTML = "<span style=\\"color: green;\\">✅ " + data.message + "</span>";'
                '            setTimeout(() => location.reload(), 1500);'
                '        }} else {{'
                '            resultDiv.innerHTML = "<span style=\\"color: red;\\">❌ " + data.error + "</span>";'
                '        }}'
                '    }})'
                '    .catch(error => {{'
                '        resultDiv.innerHTML = "<span style=\\"color: red;\\">❌ Error: " + error + "</span>";'
                '    }});'
                '}}'
                '</script>',
                obj.pk, obj.pk
            )
        else:
            return format_html(
                '<span style="color: gray;">Save challenge with reference query first</span>'
            )
    generate_output_button.short_description = "Generate Expected Output"

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

    def regenerate_expected_results(self, request, queryset):
        """Regenerate expected results for selected challenges"""
        success_count = 0
        failed_count = 0

        for challenge in queryset:
            # Only process dual-dataset challenges
            if challenge.schema_sql and challenge.submit_dataset_sql and challenge.reference_query:
                # Clear existing expected results to force regeneration
                challenge.expected_result = []
                challenge.save()  # This triggers auto-generation

                if challenge.expected_result and len(challenge.expected_result) > 0:
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1

        if success_count > 0:
            self.message_user(request, f"✅ Successfully regenerated expected results for {success_count} challenges.")
        if failed_count > 0:
            self.message_user(request, f"⚠️ Failed to regenerate expected results for {failed_count} challenges (missing schema/dataset/query).")

    regenerate_expected_results.short_description = "Regenerate expected results for dual-dataset challenges"

    def get_urls(self):
        """Add custom URLs for the admin interface"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:challenge_id>/generate-output/',
                self.admin_site.admin_view(self.generate_output_view),
                name='challenge_generate_output',
            ),
        ]
        return custom_urls + urls

    def generate_output_view(self, request, challenge_id):
        """Handle AJAX request to generate expected output JSON"""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Only POST method allowed'})

        challenge = get_object_or_404(Challenge, pk=challenge_id)

        try:
            success, message = challenge.execute_reference_query()
            return JsonResponse({
                'success': success,
                'message': message if success else None,
                'error': None if success else message
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            })


@admin.register(ChallengeTable)
class ChallengeTableAdmin(admin.ModelAdmin):
    """
    Admin interface for ChallengeTable model.
    """
    list_display = ['challenge', 'table_name', 'order', 'created_at']
    list_filter = ['challenge__difficulty', 'created_at']
    search_fields = ['challenge__title', 'table_name']
    ordering = ['challenge', 'order', 'table_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Table Information', {
            'fields': ('challenge', 'table_name', 'order')
        }),
        ('Schema Definition', {
            'fields': ('schema_sql',),
            'description': 'Define the CREATE TABLE statement for this table.'
        }),
        ('Test Dataset (Run)', {
            'fields': ('run_dataset_sql',),
            'description': 'INSERT statements for test data that users see during query testing.'
        }),
        ('Validation Dataset (Submit)', {
            'fields': ('submit_dataset_sql',),
            'description': 'INSERT statements for validation data used in final submission checking.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    """Admin interface for XP transactions"""
    list_display = ['user', 'challenge', 'transaction_type', 'xp_amount', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__email', 'user__username', 'challenge__title', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'challenge')
