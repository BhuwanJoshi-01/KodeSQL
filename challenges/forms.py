from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
import json
from .models import Challenge


class ChallengeForm(forms.ModelForm):
    """
    Form for creating and editing challenges.
    """
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='tutorial'),
        help_text="Rich text description of the challenge"
    )

    question = forms.CharField(
        widget=CKEditor5Widget(config_name='tutorial'),
        help_text="The challenge question with examples and context"
    )

    hint = forms.CharField(
        widget=CKEditor5Widget(config_name='tutorial'),
        required=False,
        help_text="Optional hint to help users solve the challenge"
    )
    
    expected_result_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter expected result as JSON array:\n[\n  {"id": 1, "name": "John"},\n  {"id": 2, "name": "Jane"}\n]'
        }),
        help_text="Expected query result as JSON array",
        label="Expected Result (JSON)"
    )
    
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'difficulty', 'question', 'hint',
            'expected_query', 'sample_data', 'is_active', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter challenge title'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'expected_query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'SELECT * FROM users WHERE age > 18;'
            }),
            'sample_data': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.sql,.json'
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
            'expected_query': 'The correct SQL solution for this challenge',
            'sample_data': 'Upload CSV or SQL file with sample data for testing',
            'order': 'Challenge order (lower numbers appear first)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing challenge, populate expected_result_text
        if self.instance and self.instance.pk and self.instance.expected_result:
            try:
                self.fields['expected_result_text'].initial = json.dumps(
                    self.instance.expected_result, indent=2
                )
            except (TypeError, ValueError):
                self.fields['expected_result_text'].initial = str(self.instance.expected_result)

    def clean_expected_result_text(self):
        """
        Validate and convert expected result text to JSON.
        """
        expected_result_text = self.cleaned_data.get('expected_result_text', '')
        
        if not expected_result_text.strip():
            return []
        
        try:
            # Try to parse as JSON
            result = json.loads(expected_result_text)
            
            # Ensure it's a list
            if not isinstance(result, list):
                raise forms.ValidationError("Expected result must be a JSON array (list)")
            
            return result
            
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON format: {str(e)}")

    def save(self, commit=True):
        """
        Save the challenge with the expected result from the text field.
        """
        challenge = super().save(commit=False)
        
        # Set expected_result from the cleaned text field
        challenge.expected_result = self.cleaned_data.get('expected_result_text', [])
        
        if commit:
            challenge.save()
        
        return challenge


class ChallengeFilterForm(forms.Form):
    """
    Form for filtering challenges in the admin list view.
    """
    DIFFICULTY_CHOICES = [('', 'All Difficulties')] + Challenge.DIFFICULTY_CHOICES
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search challenges...'
        })
    )
