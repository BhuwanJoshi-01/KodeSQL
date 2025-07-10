"""
Forms for user authentication and profile management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from allauth.account.forms import LoginForm, SignupForm
from .models import User, UserProfile
import re


class UserRegistrationForm(UserCreationForm):
    """
    User registration form.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError("First name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in first_name:
            raise ValidationError("First name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', first_name):
            raise ValidationError("First name can only contain letters.")

        # Check length
        if len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters long.")

        if len(first_name) > 30:
            raise ValidationError("First name cannot exceed 30 characters.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError("Last name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in last_name:
            raise ValidationError("Last name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', last_name):
            raise ValidationError("Last name can only contain letters.")

        # Check length
        if len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters long.")

        if len(last_name) > 30:
            raise ValidationError("Last name cannot exceed 30 characters.")

        return last_name


class UserLoginForm(forms.Form):
    """
    User login form.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise ValidationError("Invalid email or password.")

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """
    Forgot password form.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")
        return email


class PasswordResetConfirmForm(forms.Form):
    """
    Password reset confirmation form.
    """
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password',
            'autofocus': True
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Enhanced user profile form with validation.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your last name'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError("First name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in first_name:
            raise ValidationError("First name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', first_name):
            raise ValidationError("First name can only contain letters.")

        # Check length
        if len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters long.")

        if len(first_name) > 30:
            raise ValidationError("First name cannot exceed 30 characters.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError("Last name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in last_name:
            raise ValidationError("Last name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', last_name):
            raise ValidationError("Last name can only contain letters.")

        # Check length
        if len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters long.")

        if len(last_name) > 30:
            raise ValidationError("Last name cannot exceed 30 characters.")

        return last_name


class ProfilePictureForm(forms.ModelForm):
    """
    Profile picture upload form with validation.
    """
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp',
                'id': 'profile-picture-input'
            })
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (5MB limit)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")

            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if picture.content_type not in allowed_types:
                raise ValidationError("Invalid file type. Please upload a JPG, PNG, or WebP image.")

        return picture

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username


class CustomAllauthLoginForm(LoginForm):
    """
    Custom allauth login form with consistent styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent styling to allauth forms
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': field.label
            })


class CustomAllauthSignupForm(SignupForm):
    """
    Custom allauth signup form with additional fields and styling.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent styling to allauth forms
        for field_name, field in self.fields.items():
            if field_name not in ['first_name', 'last_name']:  # These already have styling
                field.widget.attrs.update({
                    'class': 'form-input',
                    'placeholder': field.label
                })

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError("First name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in first_name:
            raise ValidationError("First name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', first_name):
            raise ValidationError("First name can only contain letters.")

        # Check length
        if len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters long.")

        if len(first_name) > 30:
            raise ValidationError("First name cannot exceed 30 characters.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError("Last name is required.")

        # Check if it contains only one word (no spaces)
        if ' ' in last_name:
            raise ValidationError("Last name must be a single word without spaces.")

        # Check for valid characters (letters only, including unicode)
        if not re.match(r'^[a-zA-ZÀ-ÿĀ-žА-я\u4e00-\u9fff]+$', last_name):
            raise ValidationError("Last name can only contain letters.")

        # Check length
        if len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters long.")

        if len(last_name) > 30:
            raise ValidationError("Last name cannot exceed 30 characters.")

        return last_name

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        return user
