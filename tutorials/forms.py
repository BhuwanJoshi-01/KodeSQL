from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Tutorial, Lesson


class TutorialForm(forms.ModelForm):
    """
    Form for creating and editing tutorials.
    """
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='tutorial'),
        help_text="Rich text description with images and formatting"
    )
    
    class Meta:
        model = Tutorial
        fields = [
            'title', 'description', 'difficulty', 'icon', 
            'thumbnail', 'is_active', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tutorial title'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Material icon name (e.g., table_chart)'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'icon': 'Material Design icon name (e.g., table_chart, code, school)',
            'order': 'Lower numbers appear first',
            'thumbnail': 'Upload an image for the tutorial card'
        }


class LessonForm(forms.ModelForm):
    """
    Form for creating and editing lessons.
    """
    content = forms.CharField(
        widget=CKEditor5Widget(config_name='tutorial'),
        help_text="Rich text content with code examples and images"
    )
    
    class Meta:
        model = Lesson
        fields = [
            'tutorial', 'title', 'content', 'example_query', 
            'expected_output', 'video_url', 'attachments', 
            'order', 'is_active'
        ]
        widgets = {
            'tutorial': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson title'
            }),
            'example_query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'SELECT * FROM users;'
            }),
            'expected_output': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Expected query output or explanation'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'example_query': 'SQL query example for this lesson',
            'expected_output': 'What the query should return or explanation',
            'video_url': 'Optional video tutorial URL',
            'attachments': 'Upload supporting files (PDF, images, etc.)',
            'order': 'Lesson order within the tutorial'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active tutorials if the tutorial field exists (not in inline formset)
        if 'tutorial' in self.fields:
            self.fields['tutorial'].queryset = Tutorial.objects.filter(is_active=True)


class LessonInlineFormSet(forms.BaseInlineFormSet):
    """
    Inline formset for lessons within tutorial creation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for new forms
        for form in self.forms:
            if not form.instance.pk and 'is_active' in form.fields:
                form.fields['is_active'].initial = True


# Create the inline formset
LessonFormSet = forms.inlineformset_factory(
    Tutorial,
    Lesson,
    form=LessonForm,
    formset=LessonInlineFormSet,
    extra=0,
    can_delete=True,
    fields=['title', 'content', 'example_query', 'expected_output', 'video_url', 'order', 'is_active']
)
