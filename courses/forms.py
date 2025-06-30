from django import forms
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Course, CourseModule, CourseLesson, CourseReview


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
    Form for creating and editing course modules.
    """
    class Meta:
        model = CourseModule
        fields = ['title', 'description', 'order', 'is_active', 'is_preview']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CourseLessonForm(forms.ModelForm):
    """
    Form for creating and editing course lessons.
    """
    class Meta:
        model = CourseLesson
        fields = [
            'title', 'content', 'lesson_type', 'video_url', 'video_duration',
            'attachments', 'example_query', 'expected_output', 'practice_query',
            'duration_minutes', 'order', 'is_active', 'is_preview'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(config_name='tutorial'),
            'lesson_type': forms.Select(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'video_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'help_text': 'Duration in seconds'
            }),
            'attachments': forms.FileInput(attrs={'class': 'form-control'}),
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
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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
