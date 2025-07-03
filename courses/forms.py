from django import forms
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Course, CourseModule, CourseLesson, LessonResource, CourseReview, SubscriptionPlan



class CourseFilterForm(forms.Form):
    """
    Form for filtering courses in the public listing.
    """
    DIFFICULTY_CHOICES = [
        ('', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    COURSE_TYPE_CHOICES = [
        ('', 'All Types'),
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('premium', 'Premium'),
    ]

    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search courses...',
            'class': 'form-control'
        })
    )
    
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    course_type = forms.ChoiceField(
        choices=COURSE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CourseForm(forms.ModelForm):
    """
    Form for creating and editing courses.
    """
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'short_description', 'description', 'difficulty',
            'course_type', 'price', 'discount_price', 'thumbnail', 'preview_video',
            'duration_hours', 'skill_level', 'language', 'tags', 'category',
            'prerequisites', 'learning_outcomes', 'is_featured', 'allow_preview',
            'certificate_enabled', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 500
            }),
            'description': CKEditor5Widget(config_name='tutorial'),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'preview_video': forms.URLInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'skill_level': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated tags'
            }),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'prerequisites': CKEditor5Widget(config_name='tutorial'),
            'learning_outcomes': CKEditor5Widget(config_name='tutorial'),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'certificate_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Auto-generate slug from title
        if not self.instance.pk:
            self.fields['slug'].widget.attrs['readonly'] = True

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        # Auto-generate slug if not provided
        if not slug and title:
            slug = slugify(title)
        
        # Check for uniqueness
        if Course.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A course with this slug already exists.")
        
        return slug

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        course_type = cleaned_data.get('course_type')
        
        # Validate pricing
        if course_type in ['paid', 'premium'] and (not price or price <= 0):
            raise forms.ValidationError("Paid courses must have a price greater than 0.")
        
        if discount_price and price and discount_price >= price:
            raise forms.ValidationError("Discount price must be less than the regular price.")
        
        return cleaned_data

    def save(self, commit=True):
        course = super().save(commit=False)
        
        # Set instructor to current user if creating new course
        if not course.pk and self.user:
            course.instructor = self.user
        
        # Auto-generate slug if not provided
        if not course.slug and course.title:
            course.slug = slugify(course.title)
        
        if commit:
            course.save()
        
        return course


class CourseModuleForm(forms.ModelForm):
    """
    Enhanced form for creating and editing course modules.
    """
    class Meta:
        model = CourseModule
        fields = ['title', 'description', 'order', 'is_active', 'is_preview']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter module title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what students will learn in this module'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'help_text': 'Order in which this module appears in the course'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'tooltip',
                'title': 'Make this module visible to students'
            }),
            'is_preview': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'tooltip',
                'title': 'Allow non-enrolled users to preview this module'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

        # Auto-set order if creating new module
        if not self.instance.pk and self.course:
            from django.db import models
            last_order = CourseModule.objects.filter(course=self.course).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            self.fields['order'].initial = last_order + 1

    def save(self, commit=True):
        module = super().save(commit=False)
        if self.course:
            module.course = self.course
        if commit:
            module.save()
        return module


class CourseLessonForm(forms.ModelForm):
    """
    Enhanced form for creating and editing course lessons.
    """
    class Meta:
        model = CourseLesson
        fields = [
            'title', 'content', 'lesson_type', 'video_file', 'video_duration', 'video_thumbnail',
            'attachments', 'example_query', 'expected_output', 'practice_query',
            'duration_minutes', 'order', 'is_active', 'is_preview'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter lesson content here...'
            }),
            'lesson_type': forms.Select(attrs={
                'class': 'form-control',
                'help_text': 'Select the type of lesson content'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/webm,video/avi,video/mov',
                'help_text': 'Upload video file (MP4, WebM, AVI, MOV supported)'
            }),
            'video_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Duration in seconds (optional)',
                'help_text': 'Video duration in seconds (optional)'
            }),
            'video_thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif',
                'help_text': 'Upload custom thumbnail (auto-generated if not provided)'
            }),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control',
                'help_text': 'Legacy attachment field - use Resources section for new uploads'
            }),
            'example_query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'SELECT * FROM table_name;'
            }),
            'expected_output': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'practice_query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Query for students to practice'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'tooltip',
                'title': 'Make this lesson visible to students'
            }),
            'is_preview': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'tooltip',
                'title': 'Allow non-enrolled users to preview this lesson'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module', None)
        super().__init__(*args, **kwargs)

        # Make video_duration optional
        self.fields['video_duration'].required = False

        # Auto-set order if creating new lesson
        if not self.instance.pk and self.module:
            from django.db import models
            last_order = CourseLesson.objects.filter(module=self.module).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            self.fields['order'].initial = last_order + 1

    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Validate file size (max 500MB)
            if video_file.size > 500 * 1024 * 1024:
                raise forms.ValidationError('Video file size cannot exceed 500MB.')

            # Validate file type
            allowed_types = ['video/mp4', 'video/webm', 'video/avi', 'video/quicktime']
            if hasattr(video_file, 'content_type') and video_file.content_type not in allowed_types:
                raise forms.ValidationError('Please upload a valid video file (MP4, WebM, AVI, MOV).')

        return video_file

    def clean_video_thumbnail(self):
        thumbnail = self.cleaned_data.get('video_thumbnail')
        if thumbnail:
            # Validate file size (max 5MB)
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Thumbnail file size cannot exceed 5MB.')

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if hasattr(thumbnail, 'content_type') and thumbnail.content_type not in allowed_types:
                raise forms.ValidationError('Please upload a valid image file (JPEG, PNG, GIF).')

        return thumbnail

    def save(self, commit=True):
        lesson = super().save(commit=False)
        if self.module:
            lesson.module = self.module
        if commit:
            lesson.save()
        return lesson


class LessonResourceForm(forms.ModelForm):
    """
    Enhanced form for creating and editing lesson resources.
    """
    class Meta:
        model = LessonResource
        fields = [
            'title', 'description', 'file', 'resource_type',
            'is_downloadable', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this resource and how students should use it'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'help_text': 'Upload PDF, document, code file, dataset, or image'
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-control',
                'help_text': 'Resource type (auto-detected based on file extension)'
            }),
            'is_downloadable': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-toggle': 'tooltip',
                'title': 'Allow students to download this resource'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'help_text': 'Order in which this resource appears'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.lesson = kwargs.pop('lesson', None)
        super().__init__(*args, **kwargs)

        # Auto-set order if creating new resource
        if not self.instance.pk and self.lesson:
            from django.db import models
            last_order = LessonResource.objects.filter(lesson=self.lesson).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            self.fields['order'].initial = last_order + 1

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (max 100MB)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 100MB.')

            # Validate file type based on extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md',
                '.py', '.js', '.html', '.css', '.sql', '.java', '.cpp', '.c',
                '.csv', '.xlsx', '.json', '.xml', '.zip', '.rar',
                '.jpg', '.jpeg', '.png', '.gif', '.svg'
            ]

            file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    f'File type .{file_extension} is not supported. '
                    f'Allowed types: {", ".join(allowed_extensions)}'
                )

        return file

    def save(self, commit=True):
        resource = super().save(commit=False)
        if self.lesson:
            resource.lesson = self.lesson
        if commit:
            resource.save()
        return resource


class BulkResourceUploadForm(forms.Form):
    """
    Simple form for bulk uploading multiple resources to a lesson.
    The actual file handling is done in the template and view using request.FILES.getlist()
    """

    def __init__(self, *args, **kwargs):
        self.lesson = kwargs.pop('lesson', None)
        super().__init__(*args, **kwargs)

    def save(self, files_list):
        """Save multiple files as lesson resources"""
        if not self.lesson:
            raise ValueError('Lesson must be provided to save resources')

        if not files_list:
            raise ValueError('No files provided')

        resources = []

        # Get starting order
        from django.db import models
        last_order = LessonResource.objects.filter(lesson=self.lesson).aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0

        for i, file in enumerate(files_list):
            # Validate file size (max 100MB per file)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError(f'File {file.name} exceeds 100MB limit.')

            # Validate file extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md',
                '.py', '.js', '.html', '.css', '.sql', '.java', '.cpp', '.c',
                '.csv', '.xlsx', '.json', '.xml', '.zip', '.rar',
                '.jpg', '.jpeg', '.png', '.gif', '.svg'
            ]

            file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    f'File {file.name} has unsupported type .{file_extension}'
                )

            # Create resource title from filename
            title = file.name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()

            resource = LessonResource.objects.create(
                lesson=self.lesson,
                title=title,
                file=file,
                order=last_order + i + 1,
                is_downloadable=True
            )
            resources.append(resource)

        return resources


class CourseStructureReorderForm(forms.Form):
    """
    Form for reordering course modules and lessons.
    """
    module_orders = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='JSON data for module ordering'
    )
    lesson_orders = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='JSON data for lesson ordering'
    )

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

    def clean_module_orders(self):
        import json
        try:
            data = json.loads(self.cleaned_data['module_orders'])
            if not isinstance(data, list):
                raise forms.ValidationError('Invalid module order data')
            return data
        except (json.JSONDecodeError, KeyError):
            raise forms.ValidationError('Invalid module order data')

    def clean_lesson_orders(self):
        import json
        try:
            data = json.loads(self.cleaned_data['lesson_orders'])
            if not isinstance(data, dict):
                raise forms.ValidationError('Invalid lesson order data')
            return data
        except (json.JSONDecodeError, KeyError):
            raise forms.ValidationError('Invalid lesson order data')

    def save(self):
        if not self.course:
            raise ValueError('Course must be provided to reorder structure')

        module_orders = self.cleaned_data['module_orders']
        lesson_orders = self.cleaned_data['lesson_orders']

        # Update module orders
        for order, module_id in enumerate(module_orders, 1):
            CourseModule.objects.filter(
                id=module_id,
                course=self.course
            ).update(order=order)

        # Update lesson orders
        for module_id, lesson_list in lesson_orders.items():
            for order, lesson_id in enumerate(lesson_list, 1):
                CourseLesson.objects.filter(
                    id=lesson_id,
                    module_id=module_id,
                    module__course=self.course
                ).update(order=order)

        return True


class CourseReviewForm(forms.ModelForm):
    """
    Form for course reviews.
    """
    class Meta:
        model = CourseReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this course...'
            }),
        }


class SubscriptionPlanForm(forms.ModelForm):
    """
    Form for creating and editing subscription plans.
    """
    features = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Enter features one per line:\n• Feature 1\n• Feature 2\n• Feature 3'
        }),
        required=False,
        help_text="Enter features one per line"
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'duration', 'price', 'original_price', 'description',
            'features', 'plan_type', 'course', 'is_active', 'is_recommended',
            'sort_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Basic Plan, Premium Plan'
            }),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 (optional for discounts)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this plan includes...'
            }),
            'plan_type': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Select a course (leave blank for global plans)'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make course field optional for global plans
        self.fields['course'].required = False
        self.fields['course'].empty_label = "All Courses (Global Plan)"

        # Filter courses to only show published ones
        self.fields['course'].queryset = Course.objects.filter(status='published').order_by('title')

        # Set helpful labels and help texts
        self.fields['features'].help_text = "Enter features as a list, one per line. Use bullet points (•) for better formatting."
        self.fields['original_price'].help_text = "Set this higher than price to show discount. Leave blank if no discount."
        self.fields['sort_order'].help_text = "Lower numbers appear first in the list."
        self.fields['plan_type'].help_text = "Global plans apply to all courses, Course-specific plans apply to selected course only."

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        original_price = cleaned_data.get('original_price')
        plan_type = cleaned_data.get('plan_type')
        course = cleaned_data.get('course')

        # Validate pricing
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")

        if original_price and price and original_price <= price:
            raise forms.ValidationError("Original price must be higher than the current price to show a discount.")

        # Validate plan type and course relationship
        if plan_type == 'course_specific' and not course:
            raise forms.ValidationError("Course-specific plans must have a course selected.")

        if plan_type == 'global' and course:
            raise forms.ValidationError("Global plans should not have a specific course selected.")

        return cleaned_data

    def clean_features(self):
        features = self.cleaned_data.get('features', '')
        if features:
            # Convert text to list, splitting by lines and filtering empty lines
            feature_list = [line.strip() for line in features.split('\n') if line.strip()]
            return feature_list
        return []

    def save(self, commit=True):
        plan = super().save(commit=False)

        # Set course to None for global plans
        if plan.plan_type == 'global':
            plan.course = None

        if commit:
            plan.save()

        return plan
