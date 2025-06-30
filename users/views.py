from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.middleware.csrf import get_token
import json

from .models import User, UserProfile, UserDatabase, EmailVerificationToken
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm


def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    messages.success(request, 'Welcome back!')

                    # Create user database if it doesn't exist
                    UserDatabase.objects.get_or_create(user=user)

                    # Create user profile if it doesn't exist
                    UserProfile.objects.get_or_create(user=user)

                    next_url = request.GET.get('next', 'core:home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                    # Add a link to resend verification email
                    messages.info(request, f'<a href="/auth/resend-verification/?email={email}">Click here to resend verification email</a>')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'page_title': 'Login',
        'csrf_token': get_token(request),
    }
    return render(request, 'users/login.html', context)


def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()

            # Create user profile
            UserProfile.objects.create(user=user)

            # Create user database
            UserDatabase.objects.create(user=user)

            # Send verification email
            send_verification_email(request, user)

            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'page_title': 'Register',
        'csrf_token': get_token(request),
    }
    return render(request, 'users/register.html', context)


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def forgot_password_view(request):
    """
    Forgot password view.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_password_reset_email(request, user)
                messages.success(request, 'Password reset email sent! Please check your inbox.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            return redirect('users:login')
    else:
        form = ForgotPasswordForm()

    context = {
        'form': form,
        'page_title': 'Forgot Password',
        'csrf_token': get_token(request),
    }
    return render(request, 'users/forgot_password.html', context)


def verify_email(request, token):
    """
    Email verification view.
    """
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)

        if verification_token.is_valid:
            user = verification_token.user
            user.is_email_verified = True
            user.save()

            verification_token.is_used = True
            verification_token.save()

            messages.success(request, 'Email verified successfully! You can now log in.')
        elif verification_token.is_expired:
            messages.error(request, 'Verification link has expired. Please register again.')
        else:
            messages.error(request, 'Verification link has already been used.')

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification token.')

    return redirect('users:login')


@login_required
def profile_view(request):
    """
    User profile view.
    """
    user = request.user
    profile = user.profile

    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Profile',
    }
    return render(request, 'users/profile.html', context)


@login_required
def change_password_view(request):
    """
    Change password view.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'page_title': 'Change Password',
    }
    return render(request, 'users/change_password.html', context)


@login_required
@require_http_methods(["POST"])
def update_theme_api(request):
    """
    API endpoint to update user theme preference.
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'light')

        if theme in ['light', 'dark']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.theme_preference = theme
            profile.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid theme'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Helper functions
def send_verification_email(request, user):
    """
    Send email verification email.
    """
    # Create verification token
    verification_token = EmailVerificationToken.objects.create(user=user)

    verification_url = request.build_absolute_uri(
        reverse('users:verify_email', args=[str(verification_token.token)])
    )

    subject = 'Verify your SQL Playground account'
    message = f'''Hi {user.username},

Welcome to SQL Playground!

Please click the link below to verify your email address and activate your account:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
SQL Playground Team
'''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def resend_verification_email(request):
    """
    Resend verification email view.
    """
    email = request.GET.get('email')
    if not email:
        messages.error(request, 'Email address is required.')
        return redirect('users:login')

    try:
        user = User.objects.get(email=email)
        if user.is_email_verified:
            messages.info(request, 'Your email is already verified. You can log in now.')
            return redirect('users:login')

        # Delete old unused tokens
        EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

        # Send new verification email
        if send_verification_email(request, user):
            messages.success(request, 'Verification email sent! Please check your inbox.')
        else:
            messages.error(request, 'Failed to send verification email. Please try again later.')

    except User.DoesNotExist:
        messages.error(request, 'No account found with this email address.')

    return redirect('users:login')


def send_password_reset_email(request, user):
    """
    Send password reset email.
    """
    # This is a simplified implementation
    # In production, use Django's built-in password reset functionality
    reset_url = request.build_absolute_uri(reverse('users:forgot_password'))

    subject = 'Reset your SQL Playground password'
    message = f'''
    Hi {user.username},

    You requested a password reset for your SQL Playground account.
    Please visit: {reset_url}

    If you didn't request this, please ignore this email.

    Best regards,
    SQL Playground Team
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
