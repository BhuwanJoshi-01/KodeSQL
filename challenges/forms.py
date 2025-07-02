from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from django.contrib.auth import get_user_model
import json
from .models import Challenge, UserChallengeSubscription, ChallengeSubscriptionPlan

User = get_user_model()


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


class ChallengeSubscriptionPlanForm(forms.ModelForm):
    """
    Form for creating and editing challenge subscription plans.
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
        model = ChallengeSubscriptionPlan
        fields = [
            'name', 'duration', 'price', 'original_price', 'description',
            'features', 'is_active', 'is_recommended', 'sort_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Premium Challenge Access'
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
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this subscription plan includes...'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
        }
        help_texts = {
            'original_price': 'Optional: Show crossed-out original price for discounts',
            'description': 'Brief description of what this plan includes',
            'is_recommended': 'Mark this plan as recommended (highlighted to users)',
            'sort_order': 'Lower numbers appear first in the list'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert features list to string for display
        if self.instance and self.instance.pk and self.instance.features:
            if isinstance(self.instance.features, list):
                # Handle case where features is a list containing a string representation of a list
                if len(self.instance.features) == 1 and isinstance(self.instance.features[0], str) and self.instance.features[0].startswith('['):
                    try:
                        import ast
                        actual_features = ast.literal_eval(self.instance.features[0])
                        if isinstance(actual_features, list):
                            self.fields['features'].initial = '\n'.join(actual_features)
                        else:
                            self.fields['features'].initial = '\n'.join(self.instance.features)
                    except (ValueError, SyntaxError):
                        self.fields['features'].initial = '\n'.join(self.instance.features)
                else:
                    self.fields['features'].initial = '\n'.join(self.instance.features)

    def clean_features(self):
        """Convert features string to list"""
        features_text = self.cleaned_data.get('features', '')
        if not features_text.strip():
            return []

        # Split by lines and clean up
        features = [line.strip() for line in features_text.split('\n') if line.strip()]

        # Remove bullet points if present
        cleaned_features = []
        for feature in features:
            # Remove common bullet point characters
            feature = feature.lstrip('•·*-').strip()
            if feature:
                cleaned_features.append(feature)

        return cleaned_features


class UserChallengeSubscriptionForm(forms.ModelForm):
    """
    Form for creating and editing user challenge subscriptions.
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-placeholder': 'Select a user'
        }),
        help_text="Select the user for this subscription"
    )

    plan = forms.ModelChoiceField(
        queryset=ChallengeSubscriptionPlan.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Select the subscription plan"
    )

    class Meta:
        model = UserChallengeSubscription
        fields = [
            'user', 'plan', 'status', 'start_date', 'end_date',
            'amount_paid', 'payment_reference'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment reference (optional)'
            }),
        }
        help_texts = {
            'end_date': 'Leave blank for unlimited plans',
            'amount_paid': 'Amount paid for this subscription',
            'payment_reference': 'Optional payment reference or transaction ID'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order users by email for easier selection
        self.fields['user'].queryset = User.objects.all().order_by('email')

        # Order plans by sort_order and name
        self.fields['plan'].queryset = ChallengeSubscriptionPlan.objects.filter(
            is_active=True
        ).order_by('sort_order', 'name')


class SubscriptionFilterForm(forms.Form):
    """
    Form for filtering subscriptions in the admin list view.
    """
    STATUS_CHOICES = [('', 'All Status')] + UserChallengeSubscription.STATUS_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    plan = forms.ModelChoiceField(
        queryset=ChallengeSubscriptionPlan.objects.filter(is_active=True),
        required=False,
        empty_label="All Plans",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by user email, plan name...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order plans by sort_order and name
        self.fields['plan'].queryset = ChallengeSubscriptionPlan.objects.filter(
            is_active=True
        ).order_by('sort_order', 'name')
