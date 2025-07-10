from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.middleware.csrf import get_token
from allauth.socialaccount.models import SocialAccount
from allauth.exceptions import ImmediateHttpResponse
import json
import uuid
import os

from .models import User, UserProfile, UserDatabase, EmailVerificationToken, PasswordResetToken
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, PasswordResetConfirmForm, UserProfileForm, ProfilePictureForm


def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # Clear unverified email from session when accessing login page
    if 'unverified_email' in request.session:
        del request.session['unverified_email']

    if request.method == 'POST':
        print(f"🔍 LOGIN DEBUG: POST data received: {request.POST}")
        form = UserLoginForm(request.POST)
        print(f"🔍 LOGIN DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"🔍 LOGIN DEBUG: Form errors: {form.errors}")
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Superusers and staff don't need email verification
                if user.is_email_verified or user.is_superuser or user.is_staff:
                    login(request, user)
                    messages.success(request, 'Welcome back!')

                    # Clear any unverified email from session
                    if 'unverified_email' in request.session:
                        del request.session['unverified_email']

                    # Create user database if it doesn't exist
                    UserDatabase.objects.get_or_create(user=user)

                    # Create user profile if it doesn't exist
                    UserProfile.objects.get_or_create(user=user)

                    next_url = request.GET.get('next', 'core:dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                    # Store email in session for resend verification button
                    request.session['unverified_email'] = email
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserLoginForm()

    # Get unverified email from session if exists
    unverified_email = request.session.get('unverified_email')

    context = {
        'form': form,
        'page_title': 'Login',
        'csrf_token': get_token(request),
        'unverified_email': unverified_email,
    }
    return render(request, 'users/login.html', context)


def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        print(f"🔍 REGISTER DEBUG: POST data received: {request.POST}")
        form = UserRegistrationForm(request.POST)
        print(f"🔍 REGISTER DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"🔍 REGISTER DEBUG: Form errors: {form.errors}")
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.save()

            # Create user profile (use get_or_create in case signal already created it)
            UserProfile.objects.get_or_create(user=user)

            # Create user database (use get_or_create in case signal already created it)
            UserDatabase.objects.get_or_create(user=user)

            # Send verification email
            email_sent = send_verification_email(request, user)

            if email_sent:
                print(f"✅ SUCCESS: Registration completed for {user.email}, verification email sent")
                messages.success(request, f'🎉 Welcome to SQLMaster, {user.first_name}! Please check your email to verify your account.')
                # Redirect to email verification pending page instead of login
                return redirect('users:email_verification_pending', user_id=user.id)
            else:
                messages.warning(request, '⚠️ Registration successful! However, there was an issue sending the verification email. Please contact support or try logging in.')
                print(f"❌ WARNING: Registration completed for {user.email}, but email sending failed")
                return redirect('users:login')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f'{error}')
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')
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
    return redirect('core:landing_page')


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
                if send_password_reset_email(request, user):
                    messages.success(request, 'Password reset email sent! Please check your inbox and follow the instructions.')
                    print(f"✅ Password reset requested for {user.email}")
                else:
                    messages.error(request, 'Failed to send password reset email. Please try again later.')
                    print(f"❌ Failed to send password reset email for {user.email}")
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

            messages.success(request, f'🎉 Email verified successfully! Welcome to KodeSQL, {user.first_name or user.username}! You can now log in and start learning.')
            print(f"✅ Email verified for {user.email}")
        elif verification_token.is_expired:
            messages.error(request, 'Verification link has expired. Please register again or request a new verification email.')
            print(f"❌ Expired verification token for {verification_token.user.email}")
        else:
            messages.error(request, 'Verification link has already been used. You can log in now.')
            print(f"❌ Already used verification token for {verification_token.user.email}")

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification token. Please check the link or request a new verification email.')
        print(f"❌ Invalid verification token: {token}")

    return redirect('users:login')


def password_reset_confirm(request, token):
    """
    Password reset confirmation view.
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid:
            if reset_token.is_expired:
                messages.error(request, 'Password reset link has expired. Please request a new one.')
            else:
                messages.error(request, 'Password reset link has already been used.')
            return redirect('users:forgot_password')

        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user = reset_token.user
                new_password = form.cleaned_data['new_password1']

                # Set new password
                user.set_password(new_password)
                user.save()

                # Mark token as used
                reset_token.is_used = True
                reset_token.save()

                messages.success(request, 'Password reset successfully! You can now log in with your new password.')
                return redirect('users:login')
        else:
            form = PasswordResetConfirmForm()

        context = {
            'form': form,
            'page_title': 'Reset Password',
            'csrf_token': get_token(request),
            'user_email': reset_token.user.email,
        }
        return render(request, 'users/password_reset_confirm.html', context)

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('users:forgot_password')


def email_verification_pending(request, user_id):
    """
    Email verification pending page.
    """
    user = get_object_or_404(User, id=user_id)

    # Only show this page if the user's email is not verified
    if user.is_email_verified:
        messages.info(request, 'Your email is already verified. You can now log in.')
        return redirect('users:login')

    context = {
        'user': user,
        'page_title': 'Email Verification Pending',
    }
    return render(request, 'users/email_verification_pending.html', context)


@login_required
def profile_view(request):
    """
    Enhanced user profile view with editing capabilities.
    """
    user = request.user

    # Get or create user profile if it doesn't exist
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    # Always update total XP to ensure it's current
    profile.update_total_xp()

    # Initialize forms with default values
    profile_form = UserProfileForm(instance=user)
    picture_form = ProfilePictureForm(instance=profile)

    if request.method == 'POST':
        # Handle profile form submission
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, '🎉 Profile updated successfully!')
                return redirect('users:profile')
            else:
                messages.error(request, '❌ Please correct the errors below.')
            # Keep picture_form as initialized above

        # Handle profile picture upload
        elif 'update_picture' in request.POST:
            picture_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, '🖼️ Profile picture updated successfully!')
                return redirect('users:profile')
            else:
                messages.error(request, '❌ Please check your image file and try again.')
            # Keep profile_form as initialized above

    context = {
        'user': user,
        'profile': profile,
        'profile_form': profile_form,
        'picture_form': picture_form,
        'page_title': 'Profile',
        'csrf_token': get_token(request),
    }
    return render(request, 'users/profile.html', context)


@login_required
@require_http_methods(["POST"])
def delete_profile_picture(request):
    """
    Delete user's profile picture.
    """
    try:
        profile = request.user.profile
        if profile.profile_picture:
            profile.profile_picture.delete()
            profile.save()
            messages.success(request, '🗑️ Profile picture removed successfully!')
        else:
            messages.info(request, 'ℹ️ No profile picture to remove.')
    except Exception as e:
        messages.error(request, '❌ Failed to remove profile picture. Please try again.')
        print(f"Error deleting profile picture: {e}")

    return redirect('users:profile')


@login_required
def change_password_view(request):
    """
    Change password view.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Password changed successfully!')
            print(f"✅ Password changed successfully for user: {user.email}")
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(f"❌ Password change failed for user: {request.user.email}")
            print(f"Form errors: {form.errors}")
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
    Send email verification email with HTML template.
    """
    # Create verification token
    verification_token = EmailVerificationToken.objects.create(user=user)

    # Build verification URL using EMAIL_BASE_URL from settings to ensure correct port
    verification_path = reverse('users:verify_email', args=[str(verification_token.token)])
    verification_url = f"{settings.EMAIL_BASE_URL}{verification_path}"

    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'KodeSQL',
    }

    # Render email templates
    subject = 'Verify your KodeSQL account'
    text_content = render_to_string('emails/verification_email.txt', context)
    html_content = render_to_string('emails/verification_email.html', context)

    try:
        # Create email with both text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"✅ Verification email sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {e}")
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
            messages.success(request, '✅ Verification email sent! Please check your inbox.')
            print(f"✅ Resent verification email to {user.email}")
            # Clear the unverified email from session
            if 'unverified_email' in request.session:
                del request.session['unverified_email']
            # Redirect back to the verification pending page
            return redirect('users:email_verification_pending', user_id=user.id)
        else:
            messages.error(request, 'Failed to send verification email. Please try again later.')
            print(f"❌ Failed to resend verification email to {user.email}")

    except User.DoesNotExist:
        messages.error(request, 'No account found with this email address.')

    return redirect('users:login')


def send_password_reset_email(request, user):
    """
    Send password reset email with HTML template.
    """
    # Delete old unused tokens
    PasswordResetToken.objects.filter(user=user, is_used=False).delete()

    # Create new password reset token
    reset_token = PasswordResetToken.objects.create(user=user)

    # Build reset URL using EMAIL_BASE_URL from settings to ensure correct port
    reset_path = reverse('users:password_reset_confirm', args=[str(reset_token.token)])
    reset_url = f"{settings.EMAIL_BASE_URL}{reset_path}"

    # Email context
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'KodeSQL',
    }

    # Render email templates
    subject = 'Reset your KodeSQL password'
    text_content = render_to_string('emails/password_reset_email.txt', context)
    html_content = render_to_string('emails/password_reset_email.html', context)

    try:
        # Create email with both text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"✅ Password reset email sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send password reset email to {user.email}: {e}")
        return False


# OAuth Error Handling Views
def oauth_error_handler(request):
    """
    Handle OAuth authentication errors gracefully.
    """
    error = request.GET.get('error', 'unknown_error')
    error_description = request.GET.get('error_description', 'An unknown error occurred during authentication.')

    # Map common OAuth errors to user-friendly messages
    error_messages = {
        'access_denied': 'You cancelled the authentication process. Please try again if you want to sign in with Google.',
        'invalid_request': 'There was an issue with the authentication request. Please try again.',
        'unauthorized_client': 'The application is not authorized to use Google authentication. Please contact support.',
        'unsupported_response_type': 'Authentication method not supported. Please try email/password login.',
        'invalid_scope': 'Invalid authentication scope. Please contact support.',
        'server_error': 'Google authentication is temporarily unavailable. Please try again later or use email/password login.',
        'temporarily_unavailable': 'Google authentication is temporarily unavailable. Please try again later.',
    }

    user_message = error_messages.get(error, f'Authentication failed: {error_description}')
    messages.error(request, f'🔐 {user_message}')

    # Log the error for debugging
    print(f"❌ OAuth Error: {error} - {error_description}")

    return redirect('users:login')


def check_oauth_email_conflict(request):
    """
    Check for email conflicts between OAuth and regular accounts.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        action = request.POST.get('action')

        if not email:
            messages.error(request, 'Email address is required.')
            return redirect('users:login')

        try:
            existing_user = User.objects.get(email=email)

            if action == 'link_account':
                # User wants to link their OAuth account to existing account
                # This would typically be handled in the adapter, but we can provide
                # additional UI feedback here
                messages.info(request, 'Please log in with your existing account first, then you can link your Google account in your profile settings.')
                return redirect('users:login')

            elif action == 'use_existing':
                # User wants to use existing account
                messages.info(request, 'Please log in with your existing email and password.')
                return redirect('users:login')

        except User.DoesNotExist:
            # No conflict, proceed with OAuth
            pass

    return redirect('users:login')


@login_required
def link_social_account(request):
    """
    Allow users to link their social accounts to existing accounts.
    """
    if request.method == 'POST':
        provider = request.POST.get('provider')

        if provider == 'google':
            # Redirect to Google OAuth with linking intent
            return redirect('socialaccount_login', provider='google')

    # Show available providers to link
    context = {
        'page_title': 'Link Social Account',
        'linked_accounts': SocialAccount.objects.filter(user=request.user),
    }
    return render(request, 'users/link_social_account.html', context)


@login_required
def unlink_social_account(request, account_id):
    """
    Allow users to unlink social accounts.
    """
    try:
        social_account = SocialAccount.objects.get(id=account_id, user=request.user)
        provider_name = social_account.provider.title()
        social_account.delete()
        messages.success(request, f'✅ {provider_name} account unlinked successfully.')
    except SocialAccount.DoesNotExist:
        messages.error(request, '❌ Social account not found or you do not have permission to unlink it.')

    return redirect('users:profile')
